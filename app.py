#!/usr/bin/env python3
"""
AI Vulnerability Scanner — Web Dashboard

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

# In-memory job store: {job_id: {"status": ..., "progress": ..., "findings": [...]}}
JOBS = {}


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
    JOBS[job_id] = {
        "status": "running",
        "total": len(files),
        "done": 0,
        "findings": [],
        "current_file": None,
    }

    # NOTE: for a real production app this should run in a background worker
    # (Celery/RQ/thread). Kept synchronous-but-chunked here for demo simplicity —
    # the frontend polls /api/status/<job_id> so the UI still feels live.
    run_scan_job(job_id, extract_dir, files)

    return jsonify({"job_id": job_id})


def run_scan_job(job_id, root_dir, files):
    scanner = ClaudeVulnScanner()
    job = JOBS[job_id]
    for file_path in files:
        rel_path = os.path.relpath(file_path, root_dir)
        job["current_file"] = rel_path
        code = read_file_safely(file_path)
        language = get_language(file_path)
        findings = scanner.scan_file(rel_path, code, language)
        job["findings"].extend(findings)
        job["done"] += 1
    job["status"] = "complete"
    job["current_file"] = None


@app.route("/api/status/<job_id>")
def status(job_id):
    job = JOBS.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
