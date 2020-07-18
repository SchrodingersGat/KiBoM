#!/usr/bin/env python3
"""
    @package
    KiBOM - Bill of Materials generation for KiCad

    Generate BOM in xml, csv, txt, tsv, html or xlsx formats.

    - Components are automatically grouped into BoM rows (grouping is configurable)
    - Component groups count number of components and list component designators
    - Rows are automatically sorted by component reference(s)
    - Supports board variants

    Extended options are available in the "bom.ini" config file in the PCB directory
    (this file is auto-generated with default options the first time the script is executed).

    For usage help:
    python KiBOM_CLI.py -h
"""

import sys
import os

here = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, here)

from kibom.__main__ import main  # noqa: E402

main()
