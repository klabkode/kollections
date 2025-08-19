#!/usr/bin/env python3

# Version 1

import os
import re
import shutil
import subprocess
import http.server
import socketserver
import threading
import logging

# Configuration
SERVER_PORT = 1111
KTRACE_HOME = os.path.expanduser("~/.ktree")
RESOURCES_PATH = os.path.join(KTRACE_HOME, "res")
VIEWER_HTML = os.path.join(KTRACE_HOME, "viewer.html")

# Setup logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


def generate_index_html(title: str, ignore_patterns: list):
    """Generates `index.html` with a file tree and custom styling."""
    ignore_arg = f"-I '{'|'.join(ignore_patterns)}'" if ignore_patterns else ""

    try:
        # Run `tree` command to generate the HTML file
        subprocess.run(
            f'tree -H . -T "Diskmap-srv1: {title}" {ignore_arg} --noreport -o index.html',
            shell=True, check=True
        )
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to run `tree` command: {e}")
        return

    if not os.path.exists("index.html"):
        logging.error("index.html was not created. Check if `tree` command is installed.")
        return

    with open("index.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    # Update footer text
    html_content = re.sub(
        r'<p class="VERSION">.*?</p>',
        '<p class="VERSION">Built with Klab HTML Tree View Generator</p>',
        html_content,
        flags=re.DOTALL
    )

    # Inject custom styles for better UI
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
    html_content = html_content.replace("<head>", f"<head>\n{custom_style}", 1)

    # Update links to open in `viewer.html`
    html_content = re.sub(
        r'<a href="([^"]+)"',
        r'<a target="_blank" href="__ktree/viewer.html?file=\1"',
        html_content
    )

    with open("index.html", "w", encoding="utf-8") as file:
        file.write(html_content)

    logging.info("Generated index.html with custom styles and viewer links.")


def setup_ktree_resources():
    """Creates `__ktree/` and copies required resources."""
    os.makedirs("__ktree/res", exist_ok=True)

    # Copy `res/` folder
    dest_res_path = os.path.join("__ktree", "res")
    if os.path.exists(dest_res_path):
        shutil.rmtree(dest_res_path)
    shutil.copytree(RESOURCES_PATH, dest_res_path)

    # Copy `viewer.html`
    shutil.copy(VIEWER_HTML, os.path.join("__ktree", "viewer.html"))

    logging.info("Setup Ktree resources in '__ktree/' directory.")


def start_server(port: int):
    """Starts a reusable HTTP server to serve the generated site."""
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            logging.info("%s - %s" % (self.client_address[0], format % args))

    try:
        with socketserver.TCPServer(("", port), CustomHandler) as httpd:
            logging.info(f"Serving at http://localhost:{port}")
            httpd.serve_forever()
    except OSError as e:
        logging.error(f"Failed to start server on port {port}: {e}")


def main():
    """Main function to generate the website and start the server."""
    import sys
    args = sys.argv[1:]

    # Use current directory name as title if no arguments are given
    title = os.path.basename(os.getcwd()) if not args else args[0]
    ignore_patterns = args[1:]

    logging.info("Generating website...")
    generate_index_html(title, ignore_patterns)

    setup_ktree_resources()
    logging.info("Diskmap: Generated HTML treeview. Open 'index.html' to explore.")

    # Start HTTP server in a separate thread (non-blocking execution)
    server_thread = threading.Thread(target=start_server, args=(SERVER_PORT,), daemon=True)
    server_thread.start()

    # Keep the main thread alive to catch keyboard interrupts
    try:
        while True:
            pass
    except KeyboardInterrupt:
        logging.info("\nShutting down server...")


if __name__ == "__main__":
    main()

