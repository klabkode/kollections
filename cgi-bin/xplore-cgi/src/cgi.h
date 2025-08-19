#ifndef __XPLORE_CGI_H__
#define __XPLORE_CGI_H__

extern char htroot[];

int   cgit_init(void);
int   cgi_getconfig(const char *key, char *value);
char *cgit_get_lookup_path(void);

#endif
