#!/usr/bin/env python
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

"""

from __future__ import print_function

import sys
import os

import argparse

from bomlib.columns import ColumnList
from bomlib.netlist_reader import netlist
from bomlib.bom_writer import WriteBoM
from bomlib.preferences import BomPref

from bomlib.database import DBConnect, DBDisconnect, DBQuery

try:
    import xlsxwriter  # noqa: F401
except:
    xlsxwriter_available = False
else:
    xlsxwriter_available = True

    
def is_module_available(module_name):
    if sys.version_info < (3, 0):
        # python 2
        import importlib
        loader = importlib.find_loader(module_name)
    elif sys.version_info <= (3, 3):
        # python 3.0 to 3.3
        import pkgutil
        loader = pkgutil.find_loader(module_name)
    elif sys.version_info >= (3, 4):
        # python 3.4 and above
        from importlib import util
        loader = util.find_spec(module_name)

    return loader is not None

here = os.path.abspath(os.path.dirname(sys.argv[0]))

sys.path.append(here)
sys.path.append(os.path.join(here, "KiBOM"))


verbose = False


def close(*arg):
    print(*arg)
    sys.exit(0)


def say(*arg):
    # Simple debug message handler
    if verbose:
        print(*arg)


def isExtensionSupported(filename):
    result = False
    extensions = [".xml", ".csv", ".txt", ".tsv", ".html"]
    if xlsxwriter_available:
        extensions.append(".xlsx")
    for e in extensions:
        if filename.endswith(e):
            result = True
            break
    return result


def writeVariant(variant, subdirectory):
    if variant is not None:
        pref.pcbConfig = variant.strip().split(',')
        
    print("PCB variant: ", ", ".join(pref.pcbConfig))

    # Write preference file back out (first run will generate a file with default preferences)
    if not have_cfile:
        pref.Write(config_file)
        say("Writing preferences file %s" % (config_file,))

    # Individual components
    components = []

    # Component groups
    groups = []

    # Connect to database
    if pref.mysql_available:
        DBConnect(pref)

    # Read out the netlist
    net = netlist(input_file, prefs=pref)

    # Extract the components
    components = net.getInterestingComponents()

    if pref.mysql_available:
        # Fill additional fields from database queries
        for c in components:
            for q in pref.db_queries:
                field_name = q[0]
                field_value = DBQuery(q[1:], c, pref)
                if field_name.lower() != "none":
                    c.setField(field_name, field_value)
            break

    # Disconnect to database
    if pref.mysql_available:
        DBDisconnect(pref)

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
        say("Removing:", ColumnList.COL_GRP_BUILD_QUANTITY)

    # Finally, write the BoM out to file
    if write_to_bom:
        output_file = args.output

        if output_file is None:
            output_file = input_file.replace(".xml", ".csv")

        output_path, output_name = os.path.split(output_file)
        output_name, output_ext = os.path.splitext(output_name)

        # KiCad BOM dialog by default passes "%O" without an extension. Append our default
        if not isExtensionSupported(output_ext):
            output_ext = ".csv"

        # Make replacements to custom file_name.
        file_name = pref.outputFileName

        file_name = file_name.replace("%O", output_name)
        file_name = file_name.replace("%v", net.getVersion())
        if variant is not None:
            file_name = file_name.replace("%V", pref.variantFileNameFormat)
            file_name = file_name.replace("%V", variant)
        else:
            file_name = file_name.replace("%V", "")

        if args.subdirectory is not None:
            output_path = os.path.join(output_path, args.subdirectory)
            if not os.path.exists(os.path.abspath(output_path)):
                os.makedirs(os.path.abspath(output_path))

        output_file = os.path.join(output_path, file_name + output_ext)
        output_file = os.path.abspath(output_file)

        say("Output:", output_file)

        return WriteBoM(output_file, groups, net, columns.columns, pref)


parser = argparse.ArgumentParser(description="KiBOM Bill of Materials generator script")

parser.add_argument("netlist", help='xml netlist file. Use "%%I" when running from within KiCad')
parser.add_argument("output", default="", help='BoM output file name.\nUse "%%O" when running from within KiCad to use the default output name (csv file).\nFor e.g. HTML output, use "%%O.html"')
parser.add_argument("-n", "--number", help="Number of boards to build (default = 1)", type=int, default=None)
parser.add_argument("-v", "--verbose", help="Enable verbose output", action='count')
parser.add_argument("-r", "--variant", help="Board variant(s), used to determine which components are output to the BoM. Comma-separate for multiple.", type=str, default=None)
parser.add_argument("-d", "--subdirectory", help="Subdirectory within which to store the generated BoM files.", type=str, default=None)
parser.add_argument("--cfg", help="BoM config file (script will try to use 'bom.ini' if not specified here)")
parser.add_argument("-s", "--separator", help="CSV Separator (default ',')", type=str, default=None)

args = parser.parse_args()

input_file = args.netlist

if not input_file.endswith(".xml"):
    close("{i} is not a valid xml file".format(i=input_file))

verbose = args.verbose is not None

input_file = os.path.abspath(input_file)

say("Input:", input_file)

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

pref.mysql_available = is_module_available('mysql.connector')

have_cfile = os.path.exists(config_file)
if have_cfile:
    pref.Read(config_file)
    say("Config:", config_file)

# Pass available modules
pref.xlsxwriter_available = xlsxwriter_available

# Pass various command-line options through
pref.verbose = verbose
if args.number is not None:
    pref.boards = args.number
pref.separatorCSV = args.separator

write_to_bom = True

if args.variant is not None:
    variants = args.variant.split(';')
else:
    variants = [None]

for variant in variants:
    result = writeVariant(variant, args)
    if not result:
        sys.exit(-1)

sys.exit(0)
