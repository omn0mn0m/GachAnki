all: degeneranki.ankiaddon

degeneranki.ankiaddon:
	(cd src/degeneranki; \
	rm -r __pycache__; \
	zip $@ -FSr . -x user_files/* *__pycache__/* @; \
	mv $@ ../../build/)
