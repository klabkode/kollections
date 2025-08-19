
#include "html.h"
#include "logit.h"

void html_load_page(const char *file)
{
	size_t len = 0;
	FILE *fp = NULL;
	ssize_t nbytes = 0;
	char *line = NULL;

	do {
		if (file == NULL) {
			html_error("invalid page (null)");
			break;
		}

		if (strlen(file) <= 0) {
			html_error("invalid page name (empty)");
			break;
		}

		logit("%s", file);

		fp = fopen(file, "r");
		if (fp == NULL) {
			html_error("failed to open '%s': %s", file, strerror(errno));
			break;
		}

		while ((nbytes = getline(&line, &len, fp)) != -1) {
			html_l("%s", line);
		}

		fclose(fp);
		free(line);
	} while(0);

	return;
}

void html_hello(void)
{
	html_load_page("html/hello.html");

	return;
}

void html_init(void)
{
	html("Content-type: text/html\n");

	return;
}

/* EOF */
