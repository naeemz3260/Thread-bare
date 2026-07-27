#!/usr/bin/env python3
"""
Vantage — AI Vulnerability Scanner Web Dashboard

A small Flask app that lets you upload a .zip of a project (or point to a folder
already on the server), scans it with Claude, and shows a live results dashboard.

Run:
    export ANTHROPIC_API_KEY=sk-ant-...
    python app.py
Then open http://localhost:5000
"""

import os
import shutil
import tempfile
import uuid
import zipfile

from flask import Flask, jsonify, render_template, request

from core.claude_client import ClaudeVulnScanner
from core.file_utils import discover_source_files, get_language, read_file_safely

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = tempfile.mkdtemp(prefix="vuln_scan_")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/scan", methods=["POST"])
def start_scan():
    if "project" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["project"]
    job_id = str(uuid.uuid4())[:8]
    extract_dir = os.path.join(app.config["UPLOAD_FOLDER"], job_id)
    os.makedirs(extract_dir, exist_ok=True)

    zip_path = os.path.join(extract_dir, "project.zip")
    file.save(zip_path)

    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(extract_dir)
    except zipfile.BadZipFile:
        shutil.rmtree(extract_dir, ignore_errors=True)
        return jsonify({"error": "Uploaded file is not a valid .zip archive"}), 400

    files = discover_source_files(extract_dir)
    job = {"status": "running", "total": len(files), "done": 0, "findings": []}

    # Runs fully synchronously and returns the complete result in one response.
    # (Deliberately not using a background-job + polling split here — on
    # serverless platforms like Vercel each request can hit a different
    # function instance, so an in-memory job store can't be relied on to
    # still be there for a later poll.)
    run_scan_job(job, extract_dir, files)
    shutil.rmtree(extract_dir, ignore_errors=True)

    return jsonify(job)


def run_scan_job(job, root_dir, files):
    scanner = ClaudeVulnScanner()
    for file_path in files:
        rel_path = os.path.relpath(file_path, root_dir)
        code = read_file_safely(file_path)
        language = get_language(file_path)
        findings = scanner.scan_file(rel_path, code, language)
        job["findings"].extend(findings)
        job["done"] += 1
    job["status"] = "complete"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
