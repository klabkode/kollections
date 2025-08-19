# GNU  Makefile

PREFIX := $(HOME)/.local/bin

SRC_DIR := src

all:

clean:

install:
	mkdir -p $(PREFIX)
	install -m 755 $(SRC_DIR)/mkdiskmap.py $(PREFIX)/mkdiskmap.py
	@echo "Installed Diskmap."

uninstall:
	rm -f $(PREFIX)/mkdiskmap
	@echo "Uninstalled Diskmap."

.PHONY: install uninstall
