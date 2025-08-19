#!/usr/bin/env python3

"""
Kpass Web Server - Flask version
"""

import os
import subprocess
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='public')
CORS(app)  # Enable CORS if needed

PORT = 9002


# ---- Utility functions ----
def kpass_exec(command):
    """Execute a shell command and return (output, error, status)."""
    print(f"[EXEC] {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True
        )
        if result.returncode != 0:
            print(f"[ERROR] Command failed: {result.stderr.strip()}")
            return None, result.stderr.strip(), result.returncode
        print(f"[OUTPUT] {result.stdout.strip()}")
        return result.stdout.strip(), None, 0
    except Exception as e:
        print(f"[EXCEPTION] {e}")
        return None, str(e), 1


def require_master_key():
    """Prompt for master key if not already set."""
    if not os.getenv("KPASS_MASTER_KEY"):
        try:
            master_key = input("Enter master key: ").strip()
            if not master_key:
                raise ValueError("Master key is required.")
            os.environ["KPASS_MASTER_KEY"] = master_key
        except Exception as e:
            print(f"[FATAL] {e}")
            exit(1)


# ---- Request/Response logging ----
@app.before_request
def log_request_info():
    print("\n=== Incoming Request ===")
    print(f"URL: {request.url}")
    print(f"Method: {request.method}")
    print(f"Headers:\n{dict(request.headers)}")
    if request.method in ("POST", "PUT", "PATCH"):
        try:
            print(f"Body: {request.get_json(force=True)}")
        except Exception:
            print("Body: [Not JSON or Empty]")


@app.after_request
def log_response_info(response):
    print("\n=== Outgoing Response ===")
    print(f"Status: {response.status}")
    try:
        data = response.get_data(as_text=True)
        if len(data) > 500:
            print(f"Body: [TRUNCATED] {data[:500]} ...")
        else:
            print(f"Body: {data}")
    except Exception:
        print("Body: [Unable to decode]")
    print("=========================\n")
    return response


# ---- Routes ----
@app.route("/list", methods=["GET"])
def list_domains():
    output, error, status = kpass_exec("kpass -j -n -L")
    if status != 0:
        return jsonify({"error": error}), 500
    return output


@app.route("/domain", methods=["POST"])
def get_domain():
    data = request.get_json()
    domain = data.get("domain")
    if not domain:
        return jsonify({"error": "Domain name is required"}), 400
    output, error, status = kpass_exec(f"kpass -j -f 'NAME={domain}'")
    if status != 0:
        return jsonify({"error": error}), 500
    return output


@app.route("/grep", methods=["POST"])
def grep_entries():
    data = request.get_json()
    query = data.get("query")
    if not query:
        return jsonify({"error": "Search pattern is required"}), 400
    output, error, status = kpass_exec(f"kpass -j -g '{query}'")
    if status != 0:
        return jsonify({"error": error}), 500
    return output


@app.route("/entry", methods=["POST"])
def get_entry_post():
    data = request.get_json()
    entry_id = data.get("entry_id")
    if entry_id is None:
        return jsonify({"error": "Entry ID is required"}), 400
    output, error, status = kpass_exec(f"kpass -j -l {entry_id}")
    if status != 0:
        return jsonify({"error": error}), 500
    return output


@app.route("/entry/<entry_id>", methods=["GET"])
def get_entry(entry_id):
    if not entry_id:
        return jsonify({"error": "Entry ID is required"}), 400
    output, error, status = kpass_exec(f"kpass -j -l {entry_id}")
    if status != 0:
        return jsonify({"error": error}), 500
    return output


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_static(path):
    """Serve static files from 'public'."""
    return send_from_directory(app.static_folder, path or "index.html")


# ---- Error handlers ----
@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "404: Not Found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "500: Server Error"}), 500


# ---- Main entry ----
if __name__ == "__main__":
    require_master_key()
    app.run(host="0.0.0.0", port=PORT, debug=True)
