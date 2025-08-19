#!/usr/bin/env python3

import os
import shutil
import stat
import mimetypes
from datetime import datetime
from pathlib import Path

KTREE_DIR = "__ktree"
TEMPLATE_FILE = f"{KTREE_DIR}/treeview_template.html"
OUTPUT_FILE = f"{KTREE_DIR}/treeview.html"
INDEX_LINK = "index.html"
SHARE_SRC = os.path.expanduser("~/.local/share/ktree")
EXCLUDED_DIRS = {".git", "node_modules"}
EXCLUDED_FILE_PATTERNS = (".out", ".so", ".so.1", ".swa", ".swp", ".rej", ".orig")

def log(msg):
    print(f"[INFO] {msg}")

def human_readable_size(size):
    for unit in ['B','KiB','MiB','GiB','TiB']:
        if size < 1024.0:
            return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}PiB"

def is_excluded_file(name):
    return (
        name.startswith(".") and name in {".", ".."} or
        name.endswith("~") or
        any(name.endswith(p) for p in EXCLUDED_FILE_PATTERNS)
    )

def is_excluded_dir(name):
    return (
        name in EXCLUDED_DIRS or
        name.startswith("__") or
        name in {".", ".."}
    )

def copy_template_files():
    if not os.path.isdir(SHARE_SRC):
        print(f"[ERROR] Missing template dir: {SHARE_SRC}")
        exit(1)
    shutil.copytree(SHARE_SRC, KTREE_DIR, dirs_exist_ok=True)
    log(f"Copied template files to {KTREE_DIR}")

def generate_file_entry(filepath, base_dir):
    relpath = os.path.relpath(filepath, base_dir)
    filename = os.path.basename(filepath)

    try:
        stat_info = os.stat(filepath)
        size = human_readable_size(stat_info.st_size)
        mtime = datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M')
        mimetype, _ = mimetypes.guess_type(filepath)
        mimetype = mimetype or "unknown"
    except Exception:
        size = "?"
        mtime = "?"
        mimetype = "?"

    tooltip = f"Type: {mimetype} | Size: {size} | Modified: {mtime}"
    html = f"    <li><span class='file'><a href='#' onclick='openFile(event, \"{relpath}\")' target='main' title='{tooltip}'>{filename}</a></span></li>"
    return html

def traverse_directory(dirpath, base_dir):
    dirname = os.path.basename(dirpath)
    if is_excluded_dir(dirname):
        log(f"Skipping dir: {dirname}")
        return ""

    html = [f"    <li><span class='folder'><a target='main'>{dirname}</a></span>\n    <ul>"]

    try:
        entries = sorted(Path(dirpath).iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        for entry in entries:
            name = entry.name
            if entry.is_symlink():
                html.append(f"    <li><span class='file'><a target='main'>{name} (link)</a></span></li>")
            elif entry.is_dir():
                html.append(traverse_directory(entry, base_dir))
            elif entry.is_file() and not is_excluded_file(name):
                html.append(generate_file_entry(entry, base_dir))
            else:
                log(f"Skipped file: {entry}")
    except Exception as e:
        log(f"Error accessing {dirpath}: {e}")

    html.append("    </ul></li>")
    return "\n".join(html)

def generate_html(base_dir):
    if not os.path.isfile(TEMPLATE_FILE):
        print(f"[ERROR] Missing template file: {TEMPLATE_FILE}")
        exit(1)

    log("Building HTML file tree...")
    file_tree_html = traverse_directory(base_dir, base_dir)

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = f.read()

    content = template.replace("{file_tree}", file_tree_html)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    log(f"Generated HTML: {OUTPUT_FILE}")

def create_symlink():
    target = os.path.join(KTREE_DIR, "home.html")
    if not os.path.exists(target):
        log(f"Warning: {target} not found. Symlink skipped.")
        return
    if os.path.islink(INDEX_LINK) or os.path.exists(INDEX_LINK):
        os.remove(INDEX_LINK)
    os.symlink(target, INDEX_LINK)
    log(f"Created symlink: {INDEX_LINK} → {target}")

def main():
    os.makedirs(KTREE_DIR, exist_ok=True)
    copy_template_files()
    generate_html(os.getcwd())
    create_symlink()
    log("Done.")

if __name__ == "__main__":
    main()

