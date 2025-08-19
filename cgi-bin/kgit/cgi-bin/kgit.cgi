#!/bin/bash

source cgi-bin/cgi.sh
source cgi-bin/html.sh

logit() {
	echo -e "\e[33m$@\e[0m" >&2
}

main() {
	html_init;

	local QUERY=$QUERY_STRING
	local MODE=$(cgi_get_keyval $QUERY "page")

	logit "QUERY_STRING: $QUERY_STRING"
	logit "MODE: $MODE"

	if [ -z $MODE ]; then
		html_error "Invalid Mode"
	elif [ "$MODE" == "menu" ]; then
		cgi_display_git_menu;
	elif [ "$MODE" == "viewport" ]; then
		local TASK=$(cgi_get_keyval $QUERY "task")
		html "<h1 style='font-family:Arial'>$(basename $(cgi_get_lookup_path)):</h1>"
		cgi_display_viewport "$TASK"
	fi
}

logit "=============START============="
main $@;
logit "=============FINISH============"

exit 0
