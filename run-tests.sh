#!/bin/bash

# delete the 'default' BOM file so it gets created
rm test/bom.ini

coverage erase

# Run a simple test
coverage run -a KiBOM_CLI.py test/kibom-test.xml test/bom-out.csv

# Generate a html file
coverage run -a KiBOM_CLI.py test/kibom-test.xml test/bom-out.html

# Generate an XML file
coverage run -a KiBOM_CLI.py test/kibom-test.xml test/bom-out.xml

# Generate an XLSX file
coverage run -a KiBOM_CLI.py test/kibom-test.xml test/bom-out.xlsx

# Generate HTML code coverage output
coverage html

