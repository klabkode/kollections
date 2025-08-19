
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <limits.h>

#include "html.h"
#include "logit.h"

#define CONFIGNAME "xplore.cfg"
#define LOOKUPNAME "xplore.path"
#define size_of(x) (sizeof(x)-1)

static char configfile[PATH_MAX];
static char lookupfile[PATH_MAX];

int cgit_init(void)
{
	int retval = -1;

	logit("HTROOT: %s", HTROOT);
	logit("HTCONFIG: %s", HTCONFIG);

	/* Config file path: /usr/local/etc/xplore/xplore.cfg */
	snprintf(configfile, size_of(configfile), "%s/%s", HTCONFIG, CONFIGNAME);
	logit("HTCFGFILE=%s", configfile);

	/* Lookup file path: /usr/local/etc/xplore/xplore.path */
	snprintf(lookupfile, size_of(lookupfile), "%s/%s", HTCONFIG, LOOKUPNAME);
	logit("HTLOOKUP=%s", lookupfile);

	return retval;
}

int cgi_getconfig(const char *key, char *value)
{
	FILE      *fp = NULL;
	char     *ptr = NULL;
	char    *vptr = NULL;
	char  *tmpptr = NULL;
	char *saveptr = NULL;
	int    retval = RETERR;
	static char linebuff[LINE_MAX] = {0};

	do {
		if ((key == NULL) || (value == NULL)) {
			html_error("invalid_arguments.");
			retval = RETERR;
			break;
		}

		if ((fp = fopen(configfile, "r")) == NULL ) {
			html_error("failed to open configfile: %s (%s)", configfile, strerror(errno));
			retval = RETERR;
			break;
		}

		/* Lookup configs */
		while(fgets(linebuff, (int)(sizeof(linebuff) - 1), fp) != NULL) {
			/* Skip commented lines */
			if (linebuff[0] == '#') {
				continue;
			}

			if (strstr(linebuff, key) != NULL) {
				ptr = strtok_r(linebuff, "\n", &vptr);
				logit("config-found [%s]", ptr);
				assert(ptr != NULL);
				assert(strtok_r(ptr, "=", &tmpptr) != NULL);
				vptr = strtok_r(tmpptr, " \n#", &saveptr);
				if (vptr != NULL) {
					strcpy(value, vptr);
				}

				logit("key [%s] value [%s]", key, value);
				if (strlen(value) > 0) {
					retval = RETSXS;
					goto FINISH;
				} else {
					retval = RETERR;
					goto FINISH;
				}
			}
			memset(linebuff, 0x00, sizeof linebuff);
		}

		html_error("key-value is not exist for '%s'", key);
	} while(0);

FINISH:
	if (fp)
		fclose(fp);

	return retval;
}

char *cgit_get_lookup_path(void)
{
	FILE *fp = NULL;
	static char path[PATH_MAX] = {0};

	logit("XPLORE_LOOKUP_FILE=%s", lookupfile);

	fp = fopen(lookupfile, "r");
	if (fp == NULL) {
		html_error("failed to open '%s' (%s)", lookupfile, strerror(errno));
	} else {
		if (fgets(path, (int)size_of(path), fp) != NULL) {
			if (is_valid_string(path)) {
				path[strlen(path) - 1] = '\0';
				return path;
			}
		} else {
			html("<h4 style=\"color:Tomato\">XPLORE_LOOKUP_PATH is not set.</h4>");
		}

		fclose(fp);
	}

	return NULL;
}

/* EOF */
