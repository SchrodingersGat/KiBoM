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
import locale

from .columns import ColumnList
from .netlist_reader import netlist
from .bom_writer import WriteBoM
from .preferences import BomPref
from .version import KIBOM_VERSION
from . import debug
from .component import DNF

VARIANT_FIELD_SEPARATOR = ':'


def writeVariant(input_file, output_dir, output_file, variant, preferences):
    
    if variant is not None:
        preferences.pcbConfig = variant.strip().lower().split(',')
        
    debug.message("PCB variant:", ", ".join(preferences.pcbConfig))

    # Individual components
    components = []

    # Component groups
    groups = []

    # Read out the netlist
    net = netlist(input_file, prefs=preferences)

    # Extract the components
    components = net.getInterestingComponents()

    # Check if complex variant processing is enabled
    if preferences.complexVariant:
        # Process the variant fields
        do_not_populate = []
        for component in components:
            fields = component.getFieldNames()
            for field in fields:
                try:
                    # Find fields used for variant
                    [variant_name, field_name] = field.split(VARIANT_FIELD_SEPARATOR)
                except ValueError:
                    [variant_name, field_name] = [field, '']

                if variant_name.lower() in preferences.pcbConfig:
                    # Variant exist for component
                    variant_field_value = component.getField(field)

                    # Process no loaded option
                    if variant_field_value.lower() in DNF and not field_name:
                        do_not_populate.append(component)
                        break

                    # Write variant value to target field
                    component.setField(field_name, variant_field_value)

        # Process component dnp for specified variant
        if do_not_populate:
            updated_components = []
            for component in components:
                keep = True
                for dnp in do_not_populate:
                    # If component reference if found in dnp list: set for removal
                    if component.getRef() == dnp.getRef():
                        keep = False
                        break

                if keep:
                    # Component not in dnp list
                    updated_components.append(component)
                else:
                    # Component found in dnp list
                    do_not_populate.remove(component)

            # Finally update components list
            components = updated_components

    # Group the components
    groups = net.groupComponents(components)

    columns = ColumnList(preferences.corder)

    # Read out all available fields
    for g in groups:
        for f in g.fields:
            columns.AddColumn(f)

    # Don't add 'boards' column if only one board is specified
    if preferences.boards <= 1:
        columns.RemoveColumn(ColumnList.COL_GRP_BUILD_QUANTITY)
        debug.info("Removing:", ColumnList.COL_GRP_BUILD_QUANTITY)

    if output_file is None:
        output_file = input_file.replace(".xml", ".csv")

    output_name = os.path.basename(output_file)
    output_name, output_ext = os.path.splitext(output_name)

    # KiCad BOM dialog by default passes "%O" without an extension. Append our default
    if output_ext == "":
        output_ext = ".csv"
        debug.info("No extension supplied for output file - using .csv")
    elif output_ext not in [".xml", ".csv", ".txt", ".tsv", ".html", ".xlsx"]:
        output_ext = ".csv"
        debug.warning("Unknown extension '{e}' supplied - using .csv".format(e=output_ext))

    # Make replacements to custom file_name.
    file_name = preferences.outputFileName

    file_name = file_name.replace("%O", output_name)
    file_name = file_name.replace("%v", net.getVersion())

    if variant is not None:
        file_name = file_name.replace("%V", preferences.variantFileNameFormat)
        file_name = file_name.replace("%V", variant)
    else:
        file_name = file_name.replace("%V", "")

    output_file = os.path.join(output_dir, file_name + output_ext)
    output_file = os.path.abspath(output_file)

    debug.message("Saving BOM File:", output_file)

    return WriteBoM(output_file, groups, net, columns.columns, preferences)


def main():
    locale.setlocale(locale.LC_ALL, '')

    prog = 'KiBOM_CLI.py'
    if __name__ == '__main__':
        prog = "python -m kibom"
    parser = argparse.ArgumentParser(prog=prog, description="KiBOM Bill of Materials generator script")

    parser.add_argument("netlist", help='xml netlist file. Use "%%I" when running from within KiCad')
    parser.add_argument("output", default="", help='BoM output file name.\nUse "%%O" when running from within KiCad to use the default output name (csv file).\nFor e.g. HTML output, use "%%O.html"')
    parser.add_argument("-n", "--number", help="Number of boards to build (default = 1)", type=int, default=None)
    parser.add_argument("-v", "--verbose", help="Enable verbose output", action='count')
    parser.add_argument("-r", "--variant", help="Board variant(s), used to determine which components are output to the BoM. To specify multiple variants, with a BOM file exported for each variant, separate variants with the ';' (semicolon) character.", type=str, default=None)
    parser.add_argument("-d", "--subdirectory", help="Subdirectory within which to store the generated BoM files.", type=str, default=None)
    parser.add_argument("--cfg", help="BoM config file (script will try to use 'bom.ini' if not specified here)")
    parser.add_argument("-s", "--separator", help="CSV Separator (default ',')", type=str, default=None)
    parser.add_argument('--version', action='version', version="KiBOM Version: {v}".format(v=KIBOM_VERSION))

    args = parser.parse_args()

    # Set the global debugging level
    debug.setDebugLevel(int(args.verbose) if args.verbose is not None else debug.MSG_ERROR)

    debug.message("KiBOM version {v}".format(v=KIBOM_VERSION))
    
    input_file = os.path.abspath(args.netlist)

    input_dir = os.path.abspath(os.path.dirname(input_file))

    output_file = os.path.basename(args.output)

    if args.subdirectory is not None:
        output_dir = args.subdirectory

        if not os.path.isabs(output_dir):
            output_dir = os.path.join(input_dir, output_dir)

        # Make the directory if it does not exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

            debug.message("Creating subdirectory: '{d}'".format(d=output_dir))
    else:
        output_dir = os.path.abspath(os.path.dirname(input_file))

    debug.message("Output directory: '{d}'".format(d=output_dir))

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
        # Check if variants were defined in configuration
        if pref.pcbConfig != ['default']:
            variants = pref.pcbConfig
        else:
            variants = [None]

    # Generate BOMs for each specified variant
    for variant in variants:
        result = writeVariant(input_file, output_dir, output_file, variant, pref)
        if not result:
            debug.error("Error writing variant '{v}'".format(v=variant))
            sys.exit(-1)

    sys.exit(debug.getErrorCount())


if __name__ == '__main__':
    main()
