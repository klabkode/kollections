#!/bin/bash

source cgi-bin/git.sh

set -u

cgi_get_keyval() {
	local KEYVAL="$1"
	local KEY="$2"

	[[ $# -lt 2 ]] && return 1

	# Check if the @KEYVAL is not empty
	if [ -n "$KEYVAL" ]; then
		# Parse the @KEYVAL and iterate through key-value pairs
		IFS="&" read -ra KEYVAL_SET <<< "$KEYVAL"
		for PAIR in "${KEYVAL_SET[@]}"; do
			IFS="=" read -r K V <<< "$PAIR"
			# Check if the current key matches the desired key
			if [ "$K" == "$KEY" ]; then
				echo "$V"
				return 0  # Found the key, exit with success
			fi
		done
	fi

	# Key not found
	return 1
}

cgi_get_lookup_path() {
	LOOKUP_FILE="kgit.path"

	# Check if the file exists
	if [ ! -e "$LOOKUP_FILE" ]; then
		echo "'$LOOKUP_FILE' does not exist."
		return 1
	fi

	# Read the first line from the file
	local TEXT
	if IFS= read -r TEXT < "$LOOKUP_FILE"; then
		# Check if the line is empty
		if [ -z "$TEXT" ]; then
			echo "GITWEB_LOOKUP_PATH is not set."
			return 1
		else
			# Output the first line
			echo "$TEXT"
		fi
	else
		# Handle read error
		echo "failed to read '$LOOKUP_FILE'."
		return 1
	fi
}

cgi_display_git_menu() {
	html_load_page "html/menu.html"

}

cgi_display_viewport() {
	case $1 in
		"staged")
			cgi_process_git_staged_files
			;;
		"unstaged")
			cgi_process_git_unstaged_files
			;;
		"history")
			cgi_process_git_history
			;;
		*)
			cgi_process_git_overview
			;;
	esac
}

# EOF
