#!/bin/bash

# Build MDbook Summary:

set -u

mdbook_build_summary() {
	local SRC="src"
	local INDEX="index.md"
	local SUMMARY="$SRC/SUMMARY.md"

	if [ ! -d "$SRC" ]; then
		echo "ERROR: Invalid source path '$SRC'."
		exit 1
	fi

	mdbook_write() {
		echo -e "$@"
		echo -e "$@" >> $SUMMARY
	}

	mdbook_write_index() {
		mdbook_write "# Summary"
		cp README.md src/INDEX.md
		mdbook_write "\n[Introduction](INDEX.md)"
	}

	mdbook_write_topics() {
		local TOPICNAME
		local DIRCHAPTER="$1"
		local CHAPTER="$(basename $DIRCHAPTER)"

		if [ -z "$DIRCHAPTER" ]; then
			echo "ERROR: Invalid chapter path '$DIRCHAPTER'."
			exit 1
		fi

		for DIRTOPIC in $DIRCHAPTER/*; do
			TOPICNAME=$(basename $DIRTOPIC)
			if [ "$TOPICNAME" != "$INDEX" ]; then # Skip index file
				mdbook_write "    - [$(echo ${TOPICNAME^})]($CHAPTER/$TOPICNAME)"
			fi
		done
	}

	mdbook_write_chapters() {
		local DIRCHAPTER
		local CHAPTERNAME
		local CHAPTERINDEX

		for DIRCHAPTER in $SRC/*; do
			CHAPTERNAME=$(basename $DIRCHAPTER)
			CHAPTERINDEX=$CHAPTERNAME/$INDEX

			if [ ! -f "$CHAPTERINDEX" ]; then
				CHAPTERINDEX=""
			fi

			if [ -d "$DIRCHAPTER" ]; then # Skip regular file
				mdbook_write "\n- [$(echo ${CHAPTERNAME^})]($CHAPTERINDEX)"
				mdbook_write_topics $DIRCHAPTER
			fi
		done
	}

	echo "Writing MDbook Summary '$SUMMARY' ..."

	> $SUMMARY # Reset file

	mdbook_write_index
	mdbook_write_chapters
}

# Main starts here:
mdbook_build_summary
