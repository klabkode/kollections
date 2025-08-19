import os

# Paths
KTREE_DIR = "__ktree"                           # Ensure this folder exists
TEMPLATE_FILE = os.path.join(KTREE_DIR, "index_template.html")  # Load template from __ktree
OUTPUT_FILE = os.path.join(KTREE_DIR, "treeview.html")  # Generate the file inside __ktree
INDEX_LINK = "index.html"                       # Symlink target

# Ensure __ktree directory exists
os.makedirs(KTREE_DIR, exist_ok=True)

def generate_html_tree(directory, base_path, indent=12):
    """Recursively generates the HTML list for a given directory."""
    html = "\n" + " " * indent + "<ul>\n"
    items = sorted(os.listdir(directory))
    
    for item in items:
        item_path = os.path.join(directory, item)
        rel_path = os.path.relpath(item_path, base_path)

        if os.path.isdir(item_path):
            html += " " * (indent + 2) + f"<li><span class='folder'><a target='main'>{item}</a></span>\n"
            html += generate_html_tree(item_path, base_path, indent + 4)  # Recursive call for subdirectory
            html += " " * (indent + 2) + "</li>\n"
        else:
            html += " " * (indent + 2) + f"<li><span class='file'><a href='#' onclick='openFile(event, \"{rel_path}\")' target='main'>{item}</a></span></li>\n"
    
    html += " " * indent + "</ul>\n"
    return html

def main():
    if not os.path.exists(TEMPLATE_FILE):
        print(f"❌ Error: Template file '{TEMPLATE_FILE}' not found!")
        return

    ROOT_DIR = os.getcwd()  # Use the current working directory
    root_folder = os.path.basename(ROOT_DIR)
    file_tree_html = generate_html_tree(ROOT_DIR, ROOT_DIR)

    # Read template file
    with open(TEMPLATE_FILE, "r") as f:
        template_content = f.read()

    # Replace placeholder with generated file tree
    html_content = template_content.replace("{root_folder}", root_folder).replace("{file_tree}", file_tree_html)

    # Write final HTML output
    with open(OUTPUT_FILE, "w") as f:
        f.write(html_content)

    print(f"✅ HTML file tree generated: {OUTPUT_FILE}")

    # Create symbolic link: ln -sf __ktree/home.html ./index.html
    home_html = os.path.join(KTREE_DIR, "home.html")
    if not os.path.exists(home_html):
        open(home_html, 'w').write("<html><body><h2>Welcome to Xplore</h2></body></html>")  # Create a dummy home.html if missing

    try:
        if os.path.exists(INDEX_LINK) or os.path.islink(INDEX_LINK):
            os.remove(INDEX_LINK)
        os.symlink(home_html, INDEX_LINK)
        print(f"✅ Symlink created: {INDEX_LINK} -> {home_html}")
    except Exception as e:
        print(f"❌ Failed to create symlink: {e}")

if __name__ == "__main__":
    main()
