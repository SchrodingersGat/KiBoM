#!/usr/bin/make
PY_COV=python3-coverage
BROWSER=x-www-browser
PYTEST=pytest-3
OUT_DIR=output
SINGLE_TEST=test_bom_ok

deb:
	fakeroot dpkg-buildpackage -uc -b

deb_clean:
	fakeroot debian/rules clean

lint:
	# stop the build if there are Python syntax errors or undefined names
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --statistics

test_local: lint
	rm -rf $(OUT_DIR)
	rm -f tests/input_samples/bom.ini
	$(PY_COV) erase
	$(PYTEST) --test_dir $(OUT_DIR)
	$(PY_COV) report
	$(PY_COV) html
	$(BROWSER) htmlcov/index.html
	rm -f tests/input_samples/bom.ini

single_test:
	rm -rf pp
	$(PYTEST) --log-cli-level debug -k "$(SINGLE_TEST)" --test_dir pp
	cat pp/*/output.txt
	rm tests/input_samples/bom.ini

.PHONY: deb deb_clean
