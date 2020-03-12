#!/bin/bash

coverage erase
coverage run -a KiBOM_CLI.py test/kibom-test.xml test/out.csv

# Generate HTML code coverage output
coverage html