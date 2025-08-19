#!/usr/bin/env python3
"""
kbook_build_html_iframe.py

This script builds a static HTML UI for kBook with an iframe layout (similar to kHelp).
It:
  1. Reads SUMMARY.md from the given chapters directory.
  2. Generates a Table of Contents (TOC) HTML sidebar.
  3. Builds a JavaScript `window.chapterMap` for desktop-only subchapter navigation.
  4. Replaces placeholders in kbook_index.html.in template:
       {{TOC_HTML}}, {{TITLE_NAME}}, {{REPO_URL}}, {{DEFAULT_INDEX}}
  5. Writes the final index.html into the chapters directory.
  6. Copies `html/kbook.html` from the script’s location into <chapters_dir>/kbook.html
"""

import sys
import re
import shutil
from pathlib import Path

# Paths and constants
TEMPLATE_FILE = Path(__file__).parent / "html/index.html.in"   # HTML template
OUTPUT_NAME = "index.html"                                      # Output file name
VIEWPORT_SOURCE = Path(__file__).parent / "html" / "kbook.html" # Source file to copy
LINK_PATTERN = re.compile(r"\[\s*(.*?)\s*\]\(\s*(.*?)\s*\)")    # Matches [Title](path) in SUMMARY.md


def parse_summary(summary_path: Path):
    """
    Parse SUMMARY.md to:
      - Build TOC HTML string for sidebar.
      - Build JavaScript `window.chapterMap` for dynamic chapter display.

    Returns:
      toc_html (str): HTML for sidebar chapters and subchapters.
      chapter_map_js (str): <script> block defining window.chapterMap.
    """
    lines = summary_path.read_text(encoding="utf-8").splitlines()
    toc_blocks = []
    chapter_map = {}  # { chapter_id: [ {index, title, path}, ... ] }
    chapter_count = 0
    sub_count = 0
    current_block_lines = []
    current_chapter_id = ""
    current_chapter_title = ""

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        if line.startswith("# "):
            # Finish previous chapter block if open
            if current_block_lines:
                current_block_lines.append('</div>')
                toc_blocks.append("\n".join(current_block_lines))
                current_block_lines = []

            # Start a new chapter block
            chapter_count += 1
            sub_count = 0
            current_chapter_title = line[2:].strip()
            current_chapter_id = f"chapter_{chapter_count}"
            chapter_map[current_chapter_id] = []

            # Chapter header: clickable on desktop to show subchapters
            current_block_lines.append('<div class="toc-chapter-block">')
            current_block_lines.append(
                f'  <div class="toc-chapter" '
                f'onclick="if(window.innerWidth>768){{showSubChapters(\'{current_chapter_id}\', '
                f'\'{current_chapter_title}\', \'{chapter_count}\')}}">'
                f'{chapter_count}. {current_chapter_title}</div>'
            )

        else:
            # This is a subchapter line: [Title](path)
            match = LINK_PATTERN.search(line)
            if match:
                sub_count += 1
                title, path = match.groups()
                index = f"{chapter_count}.{sub_count}"
                esc_path = path.replace("'", "\\'")
                # Direct openFile() link
                current_block_lines.append(
                    f'  <a class="toc-sub" href="#" '
                    f'onclick="openFile(\'{esc_path}\', event); return false;">'
                    f'{index}. {title}</a>'
                )
                # Add to chapterMap
                chapter_map[current_chapter_id].append({
                    "index": index,
                    "title": title,
                    "path": path
                })

    # Close last block
    if current_block_lines:
        current_block_lines.append('</div>')
        toc_blocks.append("\n".join(current_block_lines))

    # Build JS for window.chapterMap
    js_map = "window.chapterMap = {\n"
    for cid, items in chapter_map.items():
        js_map += f'  "{cid}": [\n'
        for item in items:
            js_map += (
                f'    {{ index: "{item["index"]}", '
                f'title: "{item["title"]}", '
                f'path: "{item["path"]}" }},\n'
            )
        js_map += "  ],\n"
    js_map += "};\n"

    return "\n\n".join(toc_blocks), f"<script>\n{js_map}</script>"


def render_template(template_path: Path, context: dict) -> str:
    """
    Read template and replace placeholders with provided values.

    Args:
      template_path (Path): Path to the HTML template.
      context (dict): Placeholder name → replacement string.

    Returns:
      str: Final HTML string.
    """
    html = template_path.read_text(encoding="utf-8")
    for key, value in context.items():
        html = html.replace(f"{{{{ {key} }}}}", value)
    return html


def copy_viewport_html(dest_dir: Path):
    """
    Copy `html/kbook.html` → <chapters_dir>/kbook.html.

    Args:
      dest_dir (Path): Target chapters directory.
    """
    if not VIEWPORT_SOURCE.exists():
        print(f"[!] Warning: kbook.html not found at {VIEWPORT_SOURCE}")
        return
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(VIEWPORT_SOURCE, dest_dir / "kbook.html")


def main(chapters_dir: str, title: str = "KBook", repo_url: str = "#"):
    """
    Main build process:
      - Read SUMMARY.md
      - Generate TOC HTML and JS chapterMap
      - Render final index.html
      - Copy kbook.html
    """
    chapters_path = Path(chapters_dir)
    summary_file = chapters_path / "SUMMARY.md"
    if not summary_file.exists():
        print(f"[✗] SUMMARY.md not found in {chapters_path}")
        sys.exit(1)

    toc_html, chapter_map_js = parse_summary(summary_file)

    # Detect default index file
    default_index = ""
    for candidate in ("INDEX.md", "index.md"):
        if (chapters_path / candidate).exists():
            default_index = candidate
            break

    # Load template and render final HTML
    if not TEMPLATE_FILE.exists():
        print(f"[✗] Template not found: {TEMPLATE_FILE}")
        sys.exit(1)

    final_html = render_template(TEMPLATE_FILE, {
        "TOC_HTML": toc_html + "\n" + chapter_map_js,
        "TITLE_NAME": title,
        "REPO_URL": repo_url,
        "DEFAULT_INDEX": default_index
    })

    # Write index.html
    output_file = chapters_path / OUTPUT_NAME
    output_file.write_text(final_html, encoding="utf-8")
    print(f"[✓] Built {output_file}")

    # Copy kbook.html
    copy_viewport_html(chapters_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python kbook_build_html_iframe.py <chapters_dir> [title] [repo_url]")
        sys.exit(1)

    dir_arg = sys.argv[1]
    title_arg = sys.argv[2] if len(sys.argv) > 2 else "KBook"
    repo_arg = sys.argv[3] if len(sys.argv) > 3 else "#"

    main(dir_arg, title_arg, repo_arg)
