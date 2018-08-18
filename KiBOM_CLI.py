#!/usr/bin/env python
"""
    @package
    KiBOM - Bill of Materials generation for KiCad

    Generate BOM in xml, csv, txt, tsv or html formats.

    - Components are automatically grouped into BoM rows (grouping is configurable)
    - Component groups count number of components and list component designators
    - Rows are automatically sorted by component reference(s)
    - Supports board variants

    Extended options are available in the "bom.ini" config file in the PCB directory (this file is auto-generated with default options the first time the script is executed).

"""

from __future__ import print_function

import re
import csv
import sys
import os
import shutil

import argparse

here = os.path.abspath(os.path.dirname(sys.argv[0]))

sys.path.append(here)
sys.path.append(os.path.join(here,"KiBOM"))

from bomlib.columns import ColumnList
from bomlib.netlist_reader import *
from bomlib.bom_writer import *
from bomlib.preferences import BomPref
from partpycker import farnell
verbose = False

def close(*arg):
    print(*arg)
    sys.exit(0)

# Simple debug message handler
def say(*arg):
    if verbose:
        print(*arg)

def isExtensionSupported(filename):
    result = False
    extensions = [".xml",".csv",".txt",".tsv",".html"]
    for e in extensions:
        if filename.endswith(e):
            result = True
            break
    return result

parser = argparse.ArgumentParser(description="KiBOM Bill of Materials generator script")

parser.add_argument("netlist", help='xml netlist file. Use "%%I" when running from within KiCad')
parser.add_argument("output",  default="", help='BoM output file name.\nUse "%%O" when running from within KiCad to use the default output name (csv file).\nFor e.g. HTML output, use "%%O.html"')
parser.add_argument("-n", "--number", help="Number of boards to build (default = 1)", type=int, default=1)
parser.add_argument("-v", "--verbose", help="Enable verbose output", action='count')
parser.add_argument("-r", "--variant", help="Board variant, used to determine which components are output to the BoM", type=str, default=None)
parser.add_argument("--cfg", help="BoM config file (script will try to use 'bom.ini' if not specified here)")
parser.add_argument("-s","--separator",help="CSV Separator (default ',')",type=str, default=None)
parser.add_argument("--farnell",help="Setup for price finding on Farnell.\nUsage : --farnell APIkey [columnName = 'Farnell SKU' [storeID = uk [[decimalSep = . [API_calls_per_sec = 2]]]",nargs="+",type=str, default=None)

args = parser.parse_args()

input_file = args.netlist

if not input_file.endswith(".xml"):
    close("{i} is not a valid xml file".format(i=input_file))

verbose = args.verbose is not None

input_file = os.path.abspath(input_file)

say("Input:",input_file)

#look for a config file!
#bom.ini by default
ini = os.path.abspath(os.path.join(os.path.dirname(input_file), "bom.ini"))

config_file = ini #default value
#user can overwrite with a specific config file
if args.cfg:
    config_file = args.cfg

#read preferences from file. If file does not exists, default preferences will be used
pref = BomPref()

have_cfile = os.path.exists(config_file)
if have_cfile:
    pref.Read(config_file)
    say("Config:",config_file)

#pass various command-line options through
pref.verbose = verbose
pref.boards = args.number
pref.separatorCSV = args.separator

if args.farnell is not None :
    pref.farnell["enabled"] = True
    pref.farnell.update(zip(["api","column","store_id","decimal_separator","api_per_sec"],args.farnell))
    
if args.variant is not None:
    pref.pcbConfig = args.variant
    print("PCB variant:", args.variant)

#write preference file back out (first run will generate a file with default preferences)
if not have_cfile:
    pref.Write(config_file)
    say("Writing preferences file %s"%(config_file,))

#individual components
components = []

#component groups
groups = []

#read out the netlist
net = netlist(input_file, prefs = pref)

#extract the components
components = net.getInterestingComponents()

#group the components
groups = net.groupComponents(components)

columns = ColumnList(pref.corder)

#read out all available fields
for g in groups:
    for f in g.fields:
        columns.AddColumn(f)

if pref.farnell["enabled"] :
    print("Retrieving prices (Farnell)")
    columns.AddColumn("Unit Price")
    columns.AddColumn("OrderQty")
    
    farnell_component_list = dict()
    farnell_col = pref.farnell["column"]
    prices = dict()
    for g in groups :
        if farnell_col in g.fields :
            farnell_id = g.fields[farnell_col]
            if farnell_id is "" :
                continue
            if farnell_id not in farnell_component_list :
                farnell_component_list[farnell_id] = 0
            farnell_component_list[farnell_id] += g.getCount()* int(g.fields[ColumnList.COL_GRP_BUILD_QUANTITY])

    farnell_handler = farnell.Farnell(pref.farnell["api"],pref.farnell["store_id"],pref.farnell["api_per_sec"])
    if len(farnell_component_list) :
        try :
            prices = farnell_handler.retrieve_price(farnell_component_list)
        except Exception as e :
            print("Error ",e.message)
            print("Error while trying to retrieve Farnell prices as batch. Trying per-component at {:d} call/sec".format(pref.farnell["api_per_sec"]))
            
            for id,qty in enumerate(farnell_component_list) :
                try :
                    prices.update(farnell_handler.retrieve_price({id:qty,}))
                except :
                    say("Issue with ID ",id)
    
        for g in groups :
            if farnell_col in g.fields :
                if g.fields[farnell_col] in prices :
                    g.fields["Unit Price"] = str(prices[g.fields[farnell_col]]["unit_price"]).replace(".",pref.farnell["decimal_separator"])
                    g.fields["OrderQty"] = str(prices[g.fields[farnell_col]]["order_qty"])
    else :
        say("No farnell reference found in design")

#don't add 'boards' column if only one board is specified
if pref.boards <= 1:
    columns.RemoveColumn(ColumnList.COL_GRP_BUILD_QUANTITY)
    say("Removing:",ColumnList.COL_GRP_BUILD_QUANTITY)


    

#todo
write_to_bom = True
result = True

#Finally, write the BoM out to file
if write_to_bom:

    output_file = args.output

    if output_file is None:
        output_file = input_file.replace(".xml","_bom.csv")

    # KiCad BOM dialog by default passes "%O" without an extension. Append our default
    if not isExtensionSupported(output_file):
        output_file += "_bom.csv"

    # If required, append the schematic version number to the filename
    if pref.includeVersionNumber:
        fsplit = output_file.split(".")
        fname = ".".join(fsplit[:-1])
        fext = fsplit[-1]

        output_file = str(fname) + "_" + str(net.getVersion()) + "." + fext

    output_file = os.path.abspath(output_file)

    say("Output:",output_file)

    result = WriteBoM(output_file, groups, net, columns.columns, pref)

if result:
    sys.exit(0)
else:
    sys.exit(-1)
