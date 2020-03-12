#!/bin/bash

coverage erase

# Run a simple test
coverage run -a KiBOM_CLI.py test/kibom-test.xml test/bom-out
# Generate HTML code coverage output
coverage html

