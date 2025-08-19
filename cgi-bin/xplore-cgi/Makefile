
#****************************************#
#                                        #
#    Makefile to build Xplore package    #
#                                        #
#****************************************#

PKGNAME   :=  Xplore
ELFNAME   :=  xplore
TARGET    :=  $(ELFNAME).cgi

SRCDIR    :=  src
OBJDIR    :=  obj
SHARE     :=  share
DIRBUILD  :=  __build

HTMLROOT  :=  /xplore
PREFIX    :=  /usr/local
HTPREFIX  :=  /var/www/html
DIRCGIBIN :=  /usr/lib/cgi-bin
HTROOT    :=  $(HTPREFIX)/$(ELFNAME)
HTCONFIG  :=  $(PREFIX)/etc/$(ELFNAME)

CC        ?=  gcc
CFLAGS    += -g -O3 -MMD -fPIE \
             -DHTROOT=\"$(HTROOT)\" -DHTCONFIG=\"$(HTCONFIG)\"
LDFLAGS   += -static
LDLIBS    += -lkstat -lmagic -llzma -lbz2 -lz

WFLAGS    += -Wall -Wextra -Wstrict-prototypes -Wno-unused-parameter -Wno-unused-result # -Wpedantic
WFLAGS    += -Walloca -Warray-bounds -Wcast-align -Wcast-qual -Wconversion -Wformat=2 -Wformat-security \
             -Wimplicit-fallthrough -Wint-conversion -Wnull-dereference -Wshadow -Wshift-overflow \
             -Wstack-protector -Wstrict-overflow=4 -Wswitch-default -Wswitch-enum -Wundef -Wvla

FSTACK    := -fstack-protector-all -fstack-protector-strong

ifneq (,$(wildcard $(HOME)/.termux))
    CPPFLAGS += -DTERMUX
    WFLAGS   +=
else
    CPPFLAGS += -Wdate-time -D_FORTIFY_SOURCE=2
    WFLAGS   += -Wduplicated-branches -Wduplicated-cond -Wformat-overflow=2 -Wformat-signedness -Wformat-truncation=2 \
                -Wlogical-op -Wstringop-overflow=4 -Wtraditional-conversion -Wtrampolines -Wstack-usage=4096
    FSTACK   += -fstack-clash-protection
    FASAN    += -fsanitize=bounds-strict
endif

CFLAGS  += $(FSTACK) $(FASAN)
LDFLAGS += $(FASAN)

BOLD := $(shell tput bold)
NC   := $(shell tput sgr0)

# Xplore sources
SRCS := $(SRCDIR)/main.c $(SRCDIR)/cgi.c $(SRCDIR)/html.c $(SRCDIR)/tree.c

# Object files
OBJS := $(SRCS:%.c=$(OBJDIR)/%.o)

# Build dependencies
DEPS := $(OBJS:%.o=%.d)

# Makefile execution starts here
all: info clean $(TARGET)

info:
	@echo "$(BOLD)Building $(PKGNAME) ...$(NC)"
	@echo "COMPILER :  $(CC)"
	@echo "CFLAGS   : $(CFLAGS)"
	@echo "CPPFLAGS : $(CPPFLAGS)"
	@echo "LDFLAGS  : $(LDFLAGS)"
	@echo "LDLIBS   : $(LDLIBS)\n"

# Link object files and generate executable
$(TARGET): $(OBJS)
	@echo  "\n$(BOLD)Linking object files ...$(NC)"
	$(CC) -o $(TARGET) $(OBJS) $(LDFLAGS) $(LDLIBS)
	@echo "$(BOLD)$(PKGNAME)$(NC) build completed [$(BOLD)$(TARGET)$(NC)]"

# Build object file for each .c file
$(OBJDIR)/%.o : %.c
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) $(WFLAGS) $(CPPFLAGS) -c $< -o $@

pathconfig:
	@eval ./scripts/pathconfig.sh $(HTROOT) $(HTCONFIG) $(HTMLROOT)

install: pathconfig
	@echo "$(BOLD)Installing $(PKGNAME) ...$(NC)"
	mkdir -p $(DESTDIR)$(HTCONFIG)
	mkdir -p $(DESTDIR)$(HTROOT)
	cp -f  $(SHARE)/xplore.path $(DESTDIR)$(HTCONFIG)
	cp -rf $(SHARE)/js          $(DESTDIR)$(HTROOT)
	cp -rf $(SHARE)/html        $(DESTDIR)$(HTROOT)
	cp -f  $(SHARE)/style.css   $(DESTDIR)$(HTROOT)
	cp -f  $(SHARE)/index.html  $(DESTDIR)$(HTROOT)
	chmod a+w   $(DESTDIR)$(HTCONFIG)/xplore.path
	install -D $(TARGET)    $(DESTDIR)$(DIRCGIBIN)/$(TARGET)

uninstall:
	@echo "$(BOLD)Un-installing $(PKGNAME) ...$(NC)"
	rm -rf $(DESTDIR)$(HTCONFIG)
	rm -rf $(DESTDIR)$(HTROOT)
	rm -f  $(DESTDIR)$(DIRCGIBIN)/$(TARGET)

KTAGSDIR  := __ktags
COREFILES := core vgcore*
clean:
	rm -f  $(SHARE)/html/header.html
	rm -f  $(SHARE)/html/treeview.html
	rm -rf $(TARGET) $(OBJDIR) $(COREFILES) $(DIRBUILD) $(KTAGSDIR)

-include $(DEPS)

.PHONY: all clean info install uninstall

# EOF
