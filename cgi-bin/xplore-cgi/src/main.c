
#define _GNU_SOURCE

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <unistd.h>
#include <assert.h>

#include "cgi.h"
#include "html.h"
#include "logit.h"
#include "kstat.h"

void html_load_tree(const char *path);

char *cgi_get_keyval(char *iquery, const char *targetKey)
{
	char *token = NULL;
	char   *key = NULL;
	char *value = NULL;
	const char *delimiter = "&=";
	static char query[PATH_MAX] = {0};

	do {
		if (iquery == NULL)
			break;

		strncpy(query, iquery, sizeof(query) - 1);
		token = strtok(query, delimiter);
		while (token != NULL) {
			key = token;
			value = strtok(NULL, delimiter);
			logit("keyval: %s=%s", key,value);

			/* Is user key matched ? */
			if (strcmp(key, targetKey) == 0) {
				/* Return key value */
				/* Caller need to free this pointer */
				return value;
			}

			/* Get next set */
			token = strtok(NULL, delimiter);
		}
	} while(0);

	return NULL;
}

void cgi_serve_blank_page(void)
{
	char *filep = NULL;
	char *file = "html/header.html";

	asprintf(&file, "%s/%s", HTROOT, file);
	html_load_page(file);
	html_footer();
	free(filep);

	return;
}

void cgi_serve_file_tree(const char *path)
{
	char *filep = NULL;
	char *file = "html/treeview.html";

	asprintf(&file, "%s/%s", HTROOT, file);
	html_load_page(file);
	html_body_init();
	html_load_tree(path);
	html_body_end();
	html_footer();
	free(filep);

	return;
}

void cgi_exec(char *fmt, ...)
{
	int   retval = -1;
	size_t   len =  0;
	ssize_t read =  0;
	va_list   ap = {0};
	FILE     *fp = NULL;
	char   *line = NULL;
	char   *xcmd = NULL;

	do {
		if (fmt == NULL) {
			printf("variable input Query is NULL");
			break;
		}

		va_start(ap, fmt);
		retval = vasprintf(&xcmd, fmt, ap);
		assert(retval != -1);
		va_end(ap);

		logit("%s", xcmd);

		fp = popen(xcmd, "r");
		if (fp == NULL) {
			html_error("failed to run command '%s'", xcmd);
			break;
		}

		while ((read = getline(&line, &len, fp)) != -1) {
			line[strlen(line) - 1] = '\0';
			html("%s", line);
		}

		pclose(fp);

		if (line) {
			free(line);
		}
	} while(0);

	free(xcmd);

	return;
}

void cgi_serve_file(const char *file)
{
	kstat_t sb = {0};
	char *xcmd = NULL;
	char *syntax = "bash";

	do {
		if (file == NULL) {
			html_error("null input");
			break;
		}

		if (access(file, F_OK|R_OK) < 0) {
			html_error("access() failed: %s (%s)", file, strerror(errno));
			break;
		}

		kstat(file, &sb);

		if (strcmp(sb.extension, "c") == 0) {
			syntax = "c";
		}

		html("<h3 style=\"font-family:Courier New;color:DarkBlue\">%s:</h3>", sb.basename);

		cgi_exec("highlight -O html -l --inline-css -S %s -i %s", syntax, file);

		free(xcmd);
	} while(0);

	return;
}

int main(int argc, char **argv)
{
	char  *mode = NULL;
	char  *file = NULL;
	char  *path = NULL;
	char *query = NULL;

	logit("=========== HTML CGI RUN ===========");

	cgit_init();
	html_init();

	query = getenv("QUERY_STRING");
	logit("QUERY_STRING: '%s'", query);

	mode = cgi_get_keyval(query, "page");
	logit("get_keyval: %s", mode);

	if (mode == NULL) {
		html_error("invalid operation.");
	} else if (strcmp(mode, "tree") == 0) {
		cgi_serve_blank_page();
		path = cgit_get_lookup_path();
		if (is_valid_string(path)) {
			cgi_serve_file_tree(path);
		}
	} else if (strcmp(mode, "viewport") == 0) {
		file = cgi_get_keyval(query, "file");
		if ((file != NULL) && (strlen(file) > 0)) {
			cgi_serve_file(file);
		} else {
			cgi_serve_blank_page();
			html_printf("Select file to view!");
		}
	} else {
		cgi_serve_blank_page();
		html_error("need to implement.");
	}

	logit("===================================");

	return 0;
}

/* EOF */
