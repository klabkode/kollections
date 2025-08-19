#!/bin/bash

set -u

html() {
	echo -e "$@"                 # Output to stdout
	echo -e "\e[33m$@\e[0m" >&2  # Output to stderr
}

html_init() {
	html "Content-type: text/html\n"
}

html_header_title() {
	local TITLE=$1

	html "<!DOCTYPE html>"
	html "<html lang='en'>"
	html "<head>"
	html "<meta charset='UTF-8'>"
	html "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
	html "<title>" $TITLE "</title>"
	html "</head>"
}

html_footer() {
	html "</html>"
}

html_body_init() {
	html "<body>"
}

html_body_end() {
	html "</body>"
}

html_error() {
	html_header_title "ERROR!"
	html_body_init
	html "<h2 style='color:Tomato;'>Oops! $@ </h2>"
	html_body_end
	html_footer
}

html_print() {
	html "<p style='font-family:Courier New'> $@ </hp>"
}

html_load_page() {
	cat $@
}

# EOF
