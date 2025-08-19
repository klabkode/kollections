#!/usr/bin/env python3

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
TAGS_DIR = BASE_DIR / "tags"
TEMPLATE_FILE = BASE_DIR / "html" / "index.html.in"
OUTPUT_FILE = BASE_DIR / "index.html"
PLACEHOLDER = "{{KHELP_FILE_TREE}}"

def build_folder_html(tag: str, files: list[str]) -> str:
    html = []
    html.append("                <ul class='folder-container'>")
    html.append("                    <div class='file-item folder' onclick='toggleFolder(this)'>")
    html.append("                        <img src='html/book.png' class='file-icon'>")
    html.append("                        <div class='file-details'>")
    html.append(f"                            <div class='file-name'>{tag}</div>")
    html.append("                        </div>")
    html.append("                    </div>")
    html.append("                    <div class='file-list collapsed'>")

    for fname in files:
        #print(f"  Added {tag}/{fname} ...")
        html.append(f"                        <div class='file-item file' onclick='openFile(\"tags/{tag}/{fname}\")'>")
        html.append("                            <img src='html/page.png' class='file-icon'>")
        html.append("                            <div class='file-details'>")
        html.append(f"                                <div class='file-name'>{fname}</div>")
        html.append("                            </div>")
        html.append("                        </div>")

    html.append("                    </div>")
    html.append("                </ul>")

    return "\n".join(html)

def generate_folder_html() -> str:
    print("Building Khelp HTML site...\n")
    blocks = []

    for tag_path in sorted(TAGS_DIR.iterdir()):
        if tag_path.is_dir():
            print(f"  Adding ... {tag_path.name}")
            files = sorted(f.name for f in tag_path.iterdir() if f.is_file())
            blocks.append(build_folder_html(tag_path.name, files))

    return "\n\n".join(blocks)

def render_template():
    if not TEMPLATE_FILE.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE_FILE}")

    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    if PLACEHOLDER not in template:
        raise ValueError(f"Placeholder '{PLACEHOLDER}' not found in template.")

    folder_html = generate_folder_html()
    output = template.replace(PLACEHOLDER, folder_html)
    OUTPUT_FILE.write_text(output, encoding="utf-8")

    print(f"\n✅ Generated {OUTPUT_FILE.relative_to(BASE_DIR)}")

if __name__ == "__main__":
    render_template()

# EOF
