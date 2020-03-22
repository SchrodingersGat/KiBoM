# -*- coding: utf-8 -*-

"""
    @package
    KiBOM - Bill of Materials generation for KiCad

    Generate BOM in xml, csv, txt, tsv, html or xlsx formats.

    - Components are automatically grouped into BoM rows (grouping is configurable)
    - Component groups count number of components and list component designators
    - Rows are automatically sorted by component reference(s)
    - Supports board variants

    Extended options are available in the "bom.ini" config file in the PCB directory (this file is auto-generated with default options the first time the script is executed).

    For usage help:
    python -m kibom -h
"""

from __future__ import print_function

import sys
import os
import argparse

from .columns import ColumnList
from .netlist_reader import netlist
from .bom_writer import WriteBoM
from .preferences import BomPref
from .version import KIBOM_VERSION
from . import debug


def writeVariant(input_file, output_file, variant, subdirectory, pref):
    if variant is not None:
        pref.pcbConfig = variant.strip().split(',')
        
    debug.message("PCB variant:", ", ".join(pref.pcbConfig))

    # Individual components
    components = []

    # Component groups
    groups = []

    # Read out the netlist
    net = netlist(input_file, prefs=pref)

    # Extract the components
    components = net.getInterestingComponents()

    # Group the components
    groups = net.groupComponents(components)

    columns = ColumnList(pref.corder)

    # Read out all available fields
    for g in groups:
        for f in g.fields:
            columns.AddColumn(f)

    # Don't add 'boards' column if only one board is specified
    if pref.boards <= 1:
        columns.RemoveColumn(ColumnList.COL_GRP_BUILD_QUANTITY)
        debug.info("Removing:", ColumnList.COL_GRP_BUILD_QUANTITY)

    if output_file is None:
        output_file = input_file.replace(".xml", ".csv")

    output_path, output_name = os.path.split(output_file)
    output_name, output_ext = os.path.splitext(output_name)

    # KiCad BOM dialog by default passes "%O" without an extension. Append our default
    if output_ext == "":
        output_ext = ".csv"
        debug.info("No extension supplied for output file - using .csv")
    elif output_ext not in [".xml", ".csv", ".txt", ".tsv", ".html", ".xlsx"]:
        output_ext = ".csv"
        debug.warning("Unknown extension '{e}' supplied - using .csv".format(e=output_ext))

    # Make replacements to custom file_name.
    file_name = pref.outputFileName

    file_name = file_name.replace("%O", output_name)
    file_name = file_name.replace("%v", net.getVersion())
    if variant is not None:
        file_name = file_name.replace("%V", pref.variantFileNameFormat)
        file_name = file_name.replace("%V", variant)
    else:
        file_name = file_name.replace("%V", "")

    output_file = os.path.join(output_path, file_name + output_ext)
    output_file = os.path.abspath(output_file)

    debug.message("Output:", output_file)

    return WriteBoM(output_file, groups, net, columns.columns, pref)


def main():

    parser = argparse.ArgumentParser(description="KiBOM Bill of Materials generator script")

    parser.add_argument("netlist", help='xml netlist file. Use "%%I" when running from within KiCad')
    parser.add_argument("output", default="", help='BoM output file name.\nUse "%%O" when running from within KiCad to use the default output name (csv file).\nFor e.g. HTML output, use "%%O.html"')
    parser.add_argument("-n", "--number", help="Number of boards to build (default = 1)", type=int, default=None)
    parser.add_argument("-v", "--verbose", help="Enable verbose output", action='count')
    parser.add_argument("-r", "--variant", help="Board variant(s), used to determine which components are output to the BoM. To specify multiple variants, with a BOM file exported for each variant, separate variants with the ';' (semicolon) character.", type=str, default=None)
    parser.add_argument("-d", "--subdirectory", help="Subdirectory within which to store the generated BoM files.", type=str, default=None)
    parser.add_argument("--cfg", help="BoM config file (script will try to use 'bom.ini' if not specified here)")
    parser.add_argument("-s", "--separator", help="CSV Separator (default ',')", type=str, default=None)
    parser.add_argument('--version', action='version', version="KiBom Version: {v}".format(v=KIBOM_VERSION))

    args = parser.parse_args()

    # Set the global debugging level
    debug.setDebugLevel(int(args.verbose) if args.verbose is not None else debug.MSG_ERROR)
    
    input_file = os.path.abspath(args.netlist)

    output_file = args.output

    if args.subdirectory is not None:
        output_file = os.path.join(args.subdirectory, output_file)

    # Make the directory if it does not exist
    if not os.path.exists(os.path.abspath(output_file)):
        os.makedirs(os.path.abspath(output_file))

    if not input_file.endswith(".xml"):
        debug.error("Input file '{f}' is not an xml file".format(f=input_file), fail=True)

    if not os.path.exists(input_file) or not os.path.isfile(input_file):
        debug.error("Input file '{f}' does not exist".format(f=input_file), fail=True)

    debug.message("Input:", input_file)

    # Look for a config file!
    # bom.ini by default
    ini = os.path.abspath(os.path.join(os.path.dirname(input_file), "bom.ini"))

    # Default value
    config_file = ini

    # User can overwrite with a specific config file
    if args.cfg:
        config_file = args.cfg

    # Read preferences from file. If file does not exists, default preferences will be used
    pref = BomPref()

    have_cfile = os.path.exists(config_file)

    if have_cfile:
        pref.Read(config_file)
        debug.message("Configuration file:", config_file)
    else:
        pref.Write(config_file)
        debug.info("Writing configuration file:", config_file)

    # Pass various command-line options through
    if args.number is not None:
        pref.boards = args.number

    pref.separatorCSV = args.separator

    if args.variant is not None:
        variants = args.variant.split(';')
    else:
        variants = [None]

    # Generate BOMs for each specified variant
    for variant in variants:
        result = writeVariant(input_file, output_file, variant, args, pref)
        if not result:
            sys.exit(-1)

    sys.exit(0)


if __name__ == '__main__':
    main()
