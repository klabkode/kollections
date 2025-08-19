#!/usr/bin/env python3
import os
import sys
import time
import subprocess
from flask import Flask, send_file, jsonify, request, abort, send_from_directory, g
from pathlib import Path
from datetime import datetime
from mimetypes import guess_type

# --- Config ---
BASE_DIR = Path(sys.argv[1] if len(sys.argv) > 1 else os.getcwd()).resolve()
PORT = int(os.environ.get("PORT", 8888))
STATIC_DIR = Path(__file__).parent / 'public'

# --- App Setup ---
app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path='')

# --- Logging Helper ---
def log(*args):
    print(f"[{time.strftime('%H:%M:%S')}] ", *args)

@app.before_request
def log_request():
    g.start = time.time()
    log("---- Incoming Request ----")
    log(f"{request.method} {request.url}")
    log(f"Headers: {dict(request.headers)}")

    if request.query_string:
        log(f"Query String: {request.query_string.decode()}")

    if request.data:
        log(f"Raw Body: {request.data.decode(errors='ignore')}")
    elif request.form:
        log(f"Form Data: {request.form.to_dict()}")

    if request.files:
        for name, file in request.files.items():
            log(f"Uploaded File: {name} → {file.filename}")

@app.after_request
def log_response(response):
    duration = time.time() - g.start
    log("---- Outgoing Response ----")
    log(f"Status: {response.status}")
    log(f"Content-Type: {response.content_type}")
    try:
        if response.content_type.startswith('application/json') or response.content_type.startswith('text'):
            data = response.get_data(as_text=True)
            log(f"Response Body: {data[:1000]}")  # limit to 1000 chars
    except Exception as e:
        log(f"Error reading response body: {e}")
    log(f"Duration: {duration:.3f}s\n")
    return response

# --- Static Files ---
@app.route('/')
def index():
    return send_from_directory(STATIC_DIR, 'index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(STATIC_DIR, 'favicon.ico')

@app.route('/<path:filename>')
def serve_static_files(filename):
    return send_from_directory(STATIC_DIR, filename)

# --- Disk Usage API ---
@app.route('/api/disk-usage')
def disk_usage():
    try:
        result = subprocess.run(['df', '-h', '.'], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        disk_info = lines[1].split()

        return jsonify({
            'filesystem': disk_info[0],
            'size': disk_info[1],
            'used': disk_info[2],
            'available': disk_info[3],
            'usePercentage': disk_info[4],
            'mountedOn': disk_info[5],
        })
    except Exception as e:
        app.logger.error(f"Disk usage error: {e}")
        return jsonify(error="Unable to fetch disk usage"), 500

# --- Safe Path Join ---
def sanitize_path(request_path: str) -> Path:
    target = (BASE_DIR / request_path.strip('/')).resolve()
    if not str(target).startswith(str(BASE_DIR)):
        raise ValueError("Invalid path")
    return target

# --- Symlink-Aware Stat ---
def resolve_symlink_stats(path: Path):
    try:
        if path.is_symlink():
            path = path.resolve()
        return path.stat(), path
    except Exception as e:
        app.logger.error(f"Error resolving symlink: {e}")
        raise

# --- File Listing API ---
@app.route('/api/files')
def list_files():
    try:
        raw_path = request.args.get('path', '/')
        rel_path = raw_path.strip('/') if raw_path else ''
        target_path = BASE_DIR if rel_path == '' else sanitize_path(rel_path)

        if not target_path.is_dir():
            abort(400, "Path is not a directory")

        files = []
        for entry in target_path.iterdir():
            try:
                stat, actual_path = resolve_symlink_stats(entry)
                is_dir = actual_path.is_dir()
                files.append({
                    'name': entry.name,
                    'path': str(entry.relative_to(BASE_DIR)),
                    'isdir': is_dir,
                    'nitems': len(list(actual_path.iterdir())) if is_dir else 0,
                    'size': "0" if is_dir else f"{stat.st_size / (1024*1024):.2f} MB",
                    'modtime': datetime.fromtimestamp(stat.st_mtime).strftime('%c'),
                })
            except Exception as e:
                app.logger.warning(f"Skipping file {entry}: {e}")
        return jsonify(files)
    except Exception as e:
        app.logger.error(f"Error retrieving files: {e}")
        return jsonify(error="Unable to scan directory"), 500

# --- File Preview API ---
@app.route('/api/file')
def get_file():
    try:
        rel_path = request.args.get('path', '').lstrip('/')
        file_path = sanitize_path(rel_path)

        stat, real_path = resolve_symlink_stats(file_path)
        if not real_path.is_file():
            abort(404, "File not found")

        ext = real_path.suffix.lower()
        mimetype, _ = guess_type(real_path)

        image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']
        audio_exts = ['.mp3', '.wav', '.ogg', '.aac', '.flac', '.m4a']
        video_exts = ['.mp4', '.webm', '.ogg', '.avi', '.mkv']
        dex_exts   = ['.dex', '.sxi', '.sxa', '.sxv']
        pdf_exts   = ['.pdf']
        doc_exts   = ['.doc', '.docx']
        xdg_exts   = ['.ppt', '.pptx', '.xls', '.xlsx', '.tgz', '.tar', '.zip', '.gz']

        if ext in image_exts + audio_exts + video_exts + pdf_exts:
            return send_file(real_path, mimetype=mimetype)

        elif ext in dex_exts:
            subprocess.Popen(['DXR_', '-n', '-p', str(real_path)])
            return "Streaming...", 250

        elif ext in doc_exts:
            try:
                output = subprocess.check_output(['pandoc', str(real_path), '-t', 'html'], text=True)
                return output
            except subprocess.CalledProcessError as e:
                app.logger.error(f"Pandoc failed: {e}")
                return "Unable to render doc file", 500

        elif ext in xdg_exts:
            subprocess.Popen(['xdg-open', str(real_path)])
            return "Streaming...", 250

        else:
            with open(real_path, 'r', encoding='utf-8') as f:
                return f.read(), 200, {'Content-Type': 'text/plain'}
    except FileNotFoundError:
        return "File not found", 404
    except Exception as e:
        app.logger.error(f"Error reading file: {e}")
        return "Unable to read file", 500

# --- PWA Manifest & .well-known ---
@app.route('/manifest.json')
def manifest():
    return send_from_directory(app.static_folder, 'manifest.json')

@app.route('/.well-known/<path:filename>')
def well_known(filename):
    return send_from_directory(os.path.join(app.static_folder, '.well-known'), filename)

# --- Launch Server ---
if __name__ == '__main__':
    print(f"Serving static from: {STATIC_DIR}")
    print(f"Serving files from: {BASE_DIR}")
    print(f"Server running at http://localhost:{PORT}")
    app.run(host='0.0.0.0', port=PORT)
