#!/usr/bin/env python3

"""
Diskmap:
Generate HTML diskmap using tree command.
Improved file explorer with enhanced navigation..

Usage:
mkdiskmap "Title" [ignored_files...]

Example:
mkdiskmap "My Disk Map" node_modules .git
"""

import os
import sys
import subprocess
import re

custom_style = """
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {
            --bg-color: #D3D3D3;
            --text-color: #000000;
            --border-color: #888888;
        }
        body {
            margin: 10px;
            color: var(--text-color);
            font-family: 'Arial', sans-serif;
            background-color: var(--bg-color);
        }
        a { text-decoration: none; }
        a[href$="/"] { color: blue; font-weight: bold; }
        a:not([href$="/"]) { color: black; }
    </style>
"""

def modify_html(title, ignore_patterns):
    """Runs the `tree` command and modifies `index.html`."""
    ignore_arg = f"-I '{'|'.join(ignore_patterns)}'" if ignore_patterns else ""
    subprocess.run(f'tree -H . -T "Diskmap-v1: {title}" {ignore_arg} --noreport -o index.html', shell=True)

    """Modifies index.html to apply styles and ensure all files open in a new tab."""
    if not os.path.exists("index.html"):
        print("Error: index.html not found. Tree command might have failed.")
        return

    with open("index.html", "r", encoding="utf-8") as file:
        content = file.read()

    # Inject custom style
    content = re.sub(r"(<head>)", r"\1\n" + custom_style, content, flags=re.DOTALL)

    # Add JavaScript to open all files in a new tab
    content = re.sub(r"(</head>)", r"""
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        document.querySelectorAll("a:not([href$='/'])").forEach(link => {
            link.setAttribute("target", "_blank"); // Open all files in a new tab
        });
    });
    </script>
    \1""", content, flags=re.DOTALL)

    # Write the modified content back to index.html
    with open("index.html", "w", encoding="utf-8") as file:
        file.write(content)

def main():
    if len(sys.argv) < 2:
        title = os.path.basename(os.getcwd())  # Use current directory name as title
        ignore_patterns = []
    else:
        title = sys.argv[1]
        ignore_patterns = sys.argv[2:]  # Remaining arguments are ignored files

    modify_html(title, ignore_patterns)

    print(f"Generated Diskmap. Open './index.html' to explore the files.")

if __name__ == "__main__":
    main()

