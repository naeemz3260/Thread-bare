"""
INTENTIONALLY VULNERABLE demo application.

This file exists ONLY as a test target for the AI Vulnerability Scanner in this
repository. It contains deliberately insecure patterns (similar in spirit to
OWASP Juice Shop / DVWA) so the scanner has real findings to detect and explain.

DO NOT deploy this file anywhere reachable from the internet.
"""

import os
import pickle
import sqlite3
import subprocess

from flask import Flask, request, render_template_string

app = Flask(__name__)

# --- Vulnerability: Hardcoded secret ---
SECRET_KEY = "super-secret-admin-key-12345"
DB_PASSWORD = "admin123"


@app.route("/user")
def get_user():
    # --- Vulnerability: SQL Injection ---
    user_id = request.args.get("id")
    conn = sqlite3.connect("app.db")
    query = "SELECT * FROM users WHERE id = " + user_id
    result = conn.execute(query).fetchall()
    return str(result)


@app.route("/search")
def search():
    # --- Vulnerability: Reflected XSS ---
    term = request.args.get("q", "")
    template = f"<h1>Results for: {term}</h1>"
    return render_template_string(template)


@app.route("/ping")
def ping():
    # --- Vulnerability: Command Injection ---
    host = request.args.get("host", "127.0.0.1")
    output = subprocess.check_output(f"ping -c 1 {host}", shell=True)
    return output


@app.route("/load-profile")
def load_profile():
    # --- Vulnerability: Insecure Deserialization ---
    data = request.args.get("data")
    profile = pickle.loads(bytes.fromhex(data))
    return str(profile)


@app.route("/download")
def download():
    # --- Vulnerability: Path Traversal ---
    filename = request.args.get("file")
    with open(os.path.join("uploads", filename), "r") as f:
        return f.read()


@app.route("/admin/delete-user")
def delete_user():
    # --- Vulnerability: Broken Access Control (no auth check) ---
    user_id = request.args.get("id")
    conn = sqlite3.connect("app.db")
    conn.execute(f"DELETE FROM users WHERE id = {user_id}")
    conn.commit()
    return f"User {user_id} deleted"


if __name__ == "__main__":
    # --- Vulnerability: Debug mode enabled in what looks like production ---
    app.run(debug=True, host="0.0.0.0")
