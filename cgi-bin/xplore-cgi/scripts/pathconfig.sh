#!/bin/bash

# Checking 2 arguments since @HTMLROOT
# might be empty for 'make install-local'
if [ $# -lt 2 ]; then
	cat <<-USAGE

	ERROR: Invalid arguments.
	Usage: pathconfig <htroot> <htconfig> <htmlroot>
	       pathconfig /var/www/html/xplore /usr/local/etc/xplore /xplore

	USAGE
	exit 1
fi

HTROOT=$1
HTCONFIG=$2
HTMLROOT=$3

#echo "Configuring path ..."
#echo "HTROOT: $HTROOT"
#echo "HTCONFIG: $HTCONFIG"
#echo "HTMLROOT: $HTMLROOT"

#sed -e "s#@__HTROOT__@#$HTROOT#g" \
#    -e "s#@__HTCONFIG__@#$HTCONFIG#g" \
#	   ./share/xplore.cfg.in > ./share/xplore.cfg

sed -e "s#@__HTMLROOT__@#$HTMLROOT#g" \
	   ./share/html/header.html.in   > ./share/html/header.html

sed -e "s#@__HTMLROOT__@#$HTMLROOT#g" \
	   ./share/html/treeview.html.in > ./share/html/treeview.html
