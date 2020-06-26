run:
	$(PYTHON) ./watch.py
.PHONY: run

exe: watch.exe
.PHONY: exe

watch.exe: dist/watch_gui.exe
	cp $< $@

dist/watch_gui.exe: watch.py watch_config.py watch_gui.py
	pyinstaller --onefile watch_gui.py

.PHONY: deps
deps::
	pip install requests pyinstaller
