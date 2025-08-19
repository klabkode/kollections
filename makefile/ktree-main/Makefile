# GNU Makefile

PREFIX := $(HOME)/.local

PACKAGE   := Ktree
TARGET    := ktree-html
RELEASE   := 1.0

DIRBIN    := $(PREFIX)/bin
DIRSHARE  := $(PREFIX)/share/ktree

all:

clean:
	rm -rf __ktree index.html

install: uninstall
	mkdir -p $(DIRSHARE)
	cp -r ./share/* $(DIRSHARE)/
	install -m 755 ./src/mktree.sh $(DIRBIN)/$(TARGET)
	install -m 755 ./src/mktree.py $(DIRBIN)/$(TARGET).py

uninstall:
	rm -rf $(DIRSHARE)
	rm -f $(DIRBIN)/$(TARGET)
	rm -f $(DIRBIN)/$(TARGET).py

.PHONY: install uninstall
