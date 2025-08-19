
#define _GNU_SOURCE

#include <dirent.h>
#include "kstat.h"
#include "html.h"
#include "logit.h"

static int process_file(const kstat_t *sb)
{

	if (sb == NULL) {
		html_error("sb is null.");
		return -1;
	}

	html("    <li><span class='file'><a href='/cgi-bin/xplore.cgi?page=viewport&file=%s' target='main' title='%lu bytes'>%s</a></span></li>",
	          sb->realname, sb->size, sb->basename);

	return 0;
}

static int traverse_directory(const char *dirname)
{
	int     retval = -1;
	int   n = 0, i =  0;
	kstat_t     sb = {0};
	char *filename = NULL;
	struct dirent **namelist = NULL;

	/* Get directory entries in namelist */
	n = scandir(dirname, &namelist, 0, alphasort);
	if (n < 0) {
		html_error("scandir failed: %s (%s)", dirname, strerror(errno));
		return -1;
	}

	for (i = 0; i < n; ++i) {
		/* Skip special entries */
		if (strcmp(namelist[i]->d_name, ".") == 0 ||
				strcmp(namelist[i]->d_name, "..") == 0) {
			continue;
		}

		/* Get relative file path and store in filename buffer */
		retval = asprintf(&filename, "%s/%s", dirname, namelist[i]->d_name);
		assert(retval != -1);

		if (kstat(filename, &sb) < 0) {
			html_error("kstat failed: %s (%s)", filename, strerror(errno));
			retval = -1;
			break;
		}

		switch (sb.mode & S_IFMT) {
			case S_IFLNK:
				html("    <li><span class='file'><a target='main'>%s (link)</a></span>", sb.basename);
				break;

			case S_IFDIR:
				html("    <li><span class='folder'><a target='main'>%s</a></span>", sb.basename);
				html("  <ul>");
				traverse_directory(filename);
				html("  </ul></li>");
				break;

			case S_IFREG:
			default:
				retval = process_file(&sb);
				break;
		};

		/* Free of asprintf */
		free(filename);
		retval = 0;
	}

	/* Free scandir list items */
	for (i = 0; i < n; ++i) {
		free(namelist[i]);
	}

	/* Free scandir list */
	free(namelist);

	return retval;
}

void html_tree_worker(const char *path)
{
	kstat_t sb = {0};

	do {
		if (access(path, F_OK) < 0) {
			html_error("file is not exist: %s (%s)", path, strerror(errno));
			break;
		}

		if (kstat(path, &sb) < 0) {
			html_error("kstat failed: %s (%s)", path, strerror(errno));
			break;
		}

		switch (sb.mode & S_IFMT) {
			case S_IFLNK:
				html("    <li><span class='file'>%s (link)</a></span></li>", path);
				break;

			case S_IFDIR:
				html("    <li><span class='folder'><a target='main'>%s</a></span>", sb.basename);
				html("  <ul>");
				traverse_directory(path);
				html("  </ul></li>");
				break;

			case S_IFREG:
			default:
				process_file(&sb);
				break;
		};
	} while(0);

	return;
}

void html_load_tree(const char *path)
{
	if ((path == NULL) || ((path != NULL) && (strlen(path) <= 0))) {
		html_error("Oops! invalid path (%s)", path);
		return;
	}

	html("  <h2>Xplore:</h2>");
	html("  <div id='control'><a href='#'>Collapse</a> | <a href='#'>Expand</a></div>");
	html("  <ul id='tree' class='filetree'>");
	html_tree_worker(path);
	html("  </ul>");

	return;
}

/* EOF */
