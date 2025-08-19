#!/bin/bash

# =============================================
#  Ktree HTML file tree generator
# =============================================
# This script:
# 1. Sets up a working directory (__ktree)
# 2. Copies template files from ~/.local/share/ktree/ into __ktree
# 3. Recursively generates an HTML file tree
# 4. Creates a symbolic link to the generated file

set -e  # Exit immediately on error

# --------------------------------------------
# CONFIGURATION
# --------------------------------------------
KTREE_DIR="__ktree"                             # Working directory
TEMPLATE_FILE="$KTREE_DIR/treeview_template.html"  # Template file for HTML
OUTPUT_FILE="$KTREE_DIR/treeview.html"          # Generated HTML output
INDEX_LINK="index.html"                         # Symlink to generated file
BASE_DIR=$(pwd)                                 # Get current working directory
SHARE_SRC="$HOME/.local/share/ktree/"           # Source directory for template files
LOG_FILE="/tmp/ktree.log"                       # Log file path

# Clear log file at the beginning
> "$LOG_FILE"

# --------------------------------------------
# LOGGING FUNCTION
# --------------------------------------------

logit() {
    echo -e "$1" >&2         # Print to stderr
}

log_to_file() {
    echo -e "$1" | tee -a "$LOG_FILE" >/dev/null  # Append log to file
    echo -ne "\r\033[K$1" >&2  # Print in place (overwrite previous line)
}

# --------------------------------------------
# SETUP FUNCTIONS
# --------------------------------------------

initialize_directories() {
    logit "[INFO] Initializing KTree environment..."
    mkdir -p "$KTREE_DIR"
    logit "[INFO] Working directory created: $KTREE_DIR"
}

copy_template_files() {
    if [[ -d "$SHARE_SRC" ]]; then
        logit "[INFO] Copying files from $SHARE_SRC to $KTREE_DIR..."
        cp -r "$SHARE_SRC"* "$KTREE_DIR/" || { logit "[ERROR] Failed to copy files from $SHARE_SRC"; exit 1; }
        logit "[INFO] Template files copied successfully!"
    else
        logit "[ERROR] Required directory $SHARE_SRC not found. Exiting."
        exit 1
    fi
}

# --------------------------------------------
# FILE TREE GENERATION
# --------------------------------------------

generate_file_entry_with_stats() { # Not used to have clean UI
    local filepath="$1"
    local relpath="${filepath#$BASE_DIR/}"   # Relative path
    local filename=$(basename "$filepath")
    local size=$(stat -c%s "$filepath")
    local mtime=$(stat -c '%Y' "$filepath")

    # Human-readable size
    local size_hr=$(numfmt --to=iec-i --suffix=B "$size")
    # Human-readable time
    local time_hr=$(date -d "@$mtime" '+%Y-%m-%d %H:%M')

    log_to_file "    Processing ... $relpath"
    echo "    <li><span class='file'><a href='#' onclick='openFile(event, \"$relpath\")' target='main'>$filename</a> <small>($size_hr, $time_hr)</small></span></li>"
}

generate_file_entry() {
    local filepath="$1"
    local relpath="${filepath#$BASE_DIR/}"
    local filename=$(basename "$filepath")
    local size=$(stat -c%s "$filepath")
    local mtime=$(stat -c '%Y' "$filepath")

    local size_hr=$(numfmt --to=iec-i --suffix=B "$size")
    local time_hr=$(date -d "@$mtime" '+%Y-%m-%d %H:%M')
    local mimetype=$(file --mime-type -b "$filepath")

    local tooltip="Type: $mimetype | Size: $size_hr | Modified: $time_hr"

    log_to_file "    Processing ... $relpath"
    echo "    <li><span class='file'><a href='#' onclick='openFile(event, \"$relpath\")' target='main' title='$tooltip'>$filename</a></span></li>"
}

traverse_directory() {
    local dirpath="$1"
    local dirname=$(basename "$dirpath")

    # Skip special or excluded directories
    case "$dirname" in
        . | .. | .git | __* | node_modules)
            log_to_file "  Skipping excluded directory: $dirname"
            return
            ;;
    esac

    log_to_file "  Processing directory ... $dirname"
    echo "    <li><span class='folder'><a target='main'>${dirname}</a></span>"
    echo "    <ul>"

    shopt -s dotglob nullglob  # Include hidden files, skip if no match

    for entry in "$dirpath"/*; do
        [[ ! -e "$entry" ]] && continue  # Skip broken symlinks or nonexistent entries
        local base_entry=$(basename "$entry")

        # Skip excluded files
        case "$base_entry" in
            *.out | *.so | *.so.1 | *.swa | *.swp | *.rej | *.orig | *~)
                log_to_file "    Skipping excluded file: $base_entry"
                continue
                ;;
        esac

        if [[ -L "$entry" ]]; then
            log_to_file "  Processing symlink: $base_entry"
            echo "    <li><span class='file'><a target='main'>${base_entry} (link)</a></span></li>"
        elif [[ -d "$entry" ]]; then
            traverse_directory "$entry"
        elif [[ -f "$entry" ]]; then
            generate_file_entry "$entry"
        fi
    done

    shopt -u dotglob nullglob  # Reset shell options
    echo "    </ul></li>"
}

generate_file_tree() {
    logit "[INFO] Generating file tree structure..."
    traverse_directory "$(pwd)"
}

generate_html() {
    [[ -f "$TEMPLATE_FILE" ]] || { logit "[ERROR] Template file '$TEMPLATE_FILE' not found!"; exit 1; }

    logit "[INFO] Loading template: $TEMPLATE_FILE"
    TEMPLATE_CONTENT=$(cat "$TEMPLATE_FILE")

    logit "[INFO] Embedding generated file tree into template..."
    {
        echo "$TEMPLATE_CONTENT" | awk -v tree="$(generate_file_tree)" '{gsub("{file_tree}", tree)}1'
    } > "$OUTPUT_FILE"

    logit "\n[INFO] HTML file tree generated: $OUTPUT_FILE"
}

# --------------------------------------------
# MAIN EXECUTION
# --------------------------------------------

main() {
    initialize_directories
    copy_template_files
    generate_html

    ln -sf __ktree/home.html "$INDEX_LINK"
    logit "[INFO] Symlink created: $INDEX_LINK -> __ktree/home.html"

    logit "[INFO] Done!"
}

main
