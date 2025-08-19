#!/bin/bash

#source cgi-bin/cgi.sh

set -u

cgi_git_exec() {
	GITWEB_LOOKUP_PATH=$(cgi_get_lookup_path);
	if [ $? -ne 0 ]; then
		html_error "$GITWEB_LOOKUP_PATH"
		return 1
	fi

	logit "GITWEB_LOOKUP_PATH: $GITWEB_LOOKUP_PATH"

	bash -c "cd $GITWEB_LOOKUP_PATH && $@ | highlight -O html --inline-css -S diff"
}

cgi_process_git_overview() {
	html "<h3 style='font-family:Arial;background-color:#85C1E9'>Latest Commit:</h3>"
	cgi_git_exec "git show --stat"
}

cgi_process_git_staged_files() {
	html "<h3 style='font-family:Arial;background-color:#85C1E9'>Stagged Files:</h3>"
	cgi_git_exec "git diff --cached --name-only"

	html "\n<h3 style='font-family:Arial;background-color:#85C1E9'>File Changes:</h3>"
	cgi_git_exec "git diff --cached"
}

cgi_process_git_unstaged_files() {
	html "<h3 style='font-family:Arial;background-color:#85C1E9'>Unstaged Files:</h3>"
	cgi_git_exec "git diff --stat"

	html "\n<h3 style='font-family:Arial;background-color:#85C1E9'>File Changes:</h3>"
	cgi_git_exec "git diff"
}

cgi_process_git_history() {
	html "<h3 style='font-family:Arial;background-color:#85C1E9'>Commit History:</h3>"
	cgi_git_exec "git log"
}

# EOF
