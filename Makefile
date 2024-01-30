all: install degeneranki.ankiaddon

degeneranki.ankiaddon:
	(cd src/degeneranki; \
	rm -r __pycache__; \
	zip $@ -FSr . -x user_files/data.json user_files/database.db *__pycache__/* @; \
	mv $@ ../../build/)

install: vendorize

venv: venv/touchfile

venv/touchfile: pyproject.toml
	test -d venv || python -m venv venv
	. venv/bin/activate; pip install .[dev]
	touch venv/touchfile

vendorize: vendorize.toml venv/touchfile
	. venv/bin/activate; python-vendorize
