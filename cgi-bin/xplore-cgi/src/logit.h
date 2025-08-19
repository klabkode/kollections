#ifndef __CGI_LOGIT_H__
#define __CGI_LOGIT_H__

#undef PATH_MAX
#undef LINE_MAX

enum {
	RETERR = -1,
	RETSXS =  0,
	PATH_MAX = 1024,
	LINE_MAX = 1024,
};

#define logit(fmt, args...) (fprintf(stderr, "%17s:%-4d %17s: " fmt "\n", __FILE__, __LINE__, __func__, ##args))

#endif
