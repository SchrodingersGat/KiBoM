#!/usr/bin/env bash
# Basic run-time sanity check for KiBoM

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Common functions
source ${SCRIPT_DIR}/common.bash

# Start in kll top-level directory
cd ${SCRIPT_DIR}/..


## Tests

cmd ./KiBOM_CLI.py --help

## Tests complete


result
exit $?
