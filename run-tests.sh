#!/bin/bash

# delete the 'default' BOM file so it gets created
rm test/bom.ini

coverage erase

# Run a simple test
coverage run -a -m kibom test/kibom-test.xml test/bom-out.csv

# Generate a html file
coverage run -a -m kibom test/kibom-test.xml test/bom-out.html

# Generate an XML file
coverage run -a -m kibom test/kibom-test.xml test/bom-out.xml

# Generate an XLSX file
coverage run -a -m kibom test/kibom-test.xml test/bom-out.xlsx
# Generate a BOM file in a subdirectory
coverage run -a -m kibom test/kibom-test.xml bom-dir.csv -d bomsubdir -vvv
coverage run -a -m kibom test/kibom-test.xml bom-dir2.html -d bomsubdir/secondsubdir -vvv


# Run the sanity checker on the output BOM files
coverage run -a test/test_bom.py

# Generate HTML code coverage output
coverage html

