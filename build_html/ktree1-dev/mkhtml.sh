#!/bin/bash

# Paths
KTREE_DIR="__ktree"                         # Ensure this folder exists
TEMPLATE_FILE="$KTREE_DIR/index_template.html"  # Load template from __ktree
OUTPUT_FILE="$KTREE_DIR/treeview.html"          # Generate the file inside __ktree
INDEX_LINK="index.html"                    # Symlink target
BASE_DIR=$(pwd)                             # Get current working directory

# Ensure __ktree directory exists
mkdir -p "$KTREE_DIR"

# Function to generate file entry with openFile() JS function
generate_file_entry() {
    local filepath="$1"
    local relpath="${filepath#$BASE_DIR/}" # Remove base directory prefix
    local filename=$(basename "$filepath")

    echo "    <li><span class='file'><a href='#' onclick='openFile(event, \"$relpath\")' target='main'>$filename</a></span></li>"
}

# Function to recursively traverse directories (including hidden files)
traverse_directory() {
    local dirpath="$1"
    local dirname=$(basename "$dirpath")

    echo "    <li><span class='folder'><a target='main'>${dirname}</a></span>"
    echo "    <ul>"

    for entry in "$dirpath"/{.,}*; do
        [[ "$(basename "$entry")" == "." || "$(basename "$entry")" == ".." ]] && continue

        if [[ -L "$entry" ]]; then
            echo "    <li><span class='file'><a target='main'>$(basename "$entry") (link)</a></span></li>"
        elif [[ -d "$entry" ]]; then
            traverse_directory "$entry"
        elif [[ -f "$entry" ]]; then
            generate_file_entry "$entry"
        fi
    done

    echo "    </ul></li>"
}

# Generate the file tree HTML
generate_file_tree() {
    traverse_directory "$(pwd)"
}

# Generate the final HTML
generate_html() {
    if [[ ! -f "$TEMPLATE_FILE" ]]; then
        echo "❌ Error: Template file '$TEMPLATE_FILE' not found!"
        exit 1
    fi

    # Read the template
    TEMPLATE_CONTENT=$(cat "$TEMPLATE_FILE")

    # Generate file tree and safely replace placeholder
    {
        echo "$TEMPLATE_CONTENT" | awk -v tree="$(generate_file_tree)" '{gsub("{file_tree}", tree)}1'
    } > "$OUTPUT_FILE"

    echo "✅ HTML file tree generated: $OUTPUT_FILE"
}

# Run the script
generate_html

# Create symbolic link
ln -sf __ktree/home.html "$INDEX_LINK"
echo "✅ Symlink created: $INDEX_LINK -> __ktree/home.html"
