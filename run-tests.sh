#!/bin/bash
# python3-coverage libjs-jquery-throttle-debounce libjs-jquery-isonscreen libjs-jquery-tablesorter
# delete the 'default' BOM file so it gets created
rm test/bom.ini

COVERAGE=python3-coverage
KIBOM=./KiBOM_CLI.py
PYTHON=python3
BROWSER=x-www-browser

$COVERAGE erase

# Run a simple test
$COVERAGE run -a $KIBOM test/kibom-test.xml test/bom-out.csv

# Generate a html file
$COVERAGE run -a $KIBOM test/kibom-test.xml test/bom-out.html

# Generate an XML file
$COVERAGE run -a $KIBOM test/kibom-test.xml test/bom-out.xml

# Generate an XLSX file
$COVERAGE run -a $KIBOM test/kibom-test.xml test/bom-out.xlsx
# Generate a BOM file in a subdirectory
$COVERAGE run -a $KIBOM test/kibom-test.xml bom-dir.csv -d bomsubdir -vvv
$COVERAGE run -a $KIBOM test/kibom-test.xml bom-dir2.html -d bomsubdir/secondsubdir -vvv


# Run the sanity checker on the output BOM files
$PYTHON test/test_bom.py

# Generate HTML code coverage output
$COVERAGE html
$BROWSER htmlcov/index.html
