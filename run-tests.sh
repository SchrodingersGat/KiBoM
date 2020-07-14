#!/bin/bash
# python3-coverage libjs-jquery-throttle-debounce libjs-jquery-isonscreen libjs-jquery-tablesorter
# delete the 'default' BOM file so it gets created
rm test/bom.ini

COVERAGE=python3-coverage

$COVERAGE erase

# Run a simple test
$COVERAGE run -a -m kibom test/kibom-test.xml test/bom-out.csv

# Generate a html file
$COVERAGE run -a -m kibom test/kibom-test.xml test/bom-out.html

# Generate an XML file
$COVERAGE run -a -m kibom test/kibom-test.xml test/bom-out.xml

# Generate an XLSX file
$COVERAGE run -a -m kibom test/kibom-test.xml test/bom-out.xlsx

# Run the sanity checker on the output BOM files
$COVERAGE run -a test/test_bom.py

# Generate HTML code coverage output
$COVERAGE html

