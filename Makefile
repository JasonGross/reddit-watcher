PYTHON?=python

run:
	$(PYTHON) ./watch.py
.PHONY: run

EXE:=$(shell $(PYTHON) -c 'from PyInstaller.compat import is_win, is_cygwin; print(".exe" if is_win or is_cygwin else "")')

exe: watch$(EXE)
.PHONY: exe

copy-exe: watch$(EXE)
	mkdir -p "$(OUTPUT)"
	cp watch$(EXE) "$(patsubst %/,%,$(OUTPUT))/"
.PHONY: copy-exe

watch$(EXE): dist/watch_gui$(EXE)
	cp $< $@

dist/watch_gui$(EXE): watch.py watch_config.py watch_gui.py watch_version.py
	pyinstaller --onefile watch_gui.py

.PHONY: update-version
update-version:
	$(PYTHON) ./update_version.py

.PHONY: deps
deps::
	pip install requests pyinstaller
