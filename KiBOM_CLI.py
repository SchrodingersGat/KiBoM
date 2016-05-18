from __future__ import print_function

import re
import csv
import sys
import os
import shutil

import argparse

here = os.path.abspath(os.path.dirname(sys.argv[0]))

sys.path.append(here)

from KiBOM.columns import ColumnList
from KiBOM.netlist_reader import *
from KiBOM.bom_writer import *
from KiBOM.preferences import BomPref

verbose = False

def close(*arg):
    print(*arg)
    sys.exit(0)
    
def say(*arg):
    if verbose:
        print(*arg)
    
parser = argparse.ArgumentParser(description="KiBOM Bill of Materials generator script")

parser.add_argument("netlist", help='xml netlist file. Use "%%I" when running from within KiCad')
parser.add_argument("--output", "-o", help='BoM output file name.\nUse "%%O" when running from within KiCad to use the default output name (csv file).\nFor e.g. HTML output, use "%%O.html"\r\nIf output file is unspecified, default output filename (csv format) will be used', default=None)

parser.add_argument("-v", "--verbose", help="Enable verbose output", action='count')
parser.add_argument("--cfg", help="BoM config file (script will try to use 'bom.ini' if not specified here)")

args = parser.parse_args()
    
input_file = args.netlist

if not input_file.endswith(".xml"):
    close("{i} is not a valid xml file".format(i=input_file))
    
verbose = args.verbose is not None
    
input_file = os.path.abspath(input_file)

say("Input:",input_file)

output_file = args.output

if output_file is None:
    output_file = input_file.replace(".xml","_bom.csv")
   
#enfore a proper extension
valid = False
extensions = [".xml",".csv",".txt",".tsv",".html"]
for e in extensions:
    if output_file.endswith(e):
        valid = True
        break
if not valid:
    close("Extension must be one of",extensions)
   
output_file = os.path.abspath(output_file)

say("Output:",output_file)
   
#look for a config file!
#bom.ini by default
config_file = os.path.abspath(os.path.join(os.path.dirname(input_file), "bom.ini"))

#user can overwrite with a specific config file
if args.cfg:
    config_file = args.cfg

#read preferences from file. If file does not exists, default preferences will be used
pref = BomPref()

#verbosity options
pref.verbose = verbose

if os.path.exists(config_file):
    pref.Read(config_file)
    say("Config:",config_file)

#write preference file back out (first run will generate a file with default preferences)
if not os.path.exists("bom.ini"):
    pref.Write("bom.ini")

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

columns = ColumnList()

#read out all available fields
for g in groups:
    for f in g.fields:
        columns.AddColumn(f)

if pref.buildNumber < 1:
    columns.RemoveColumn(ColumnList.COL_GRP_BUILD_QUANTITY)
    say("Removing:",ColumnList.COL_GRP_BUILD_QUANTITY)
        
#Finally, write the BoM out to file
result = WriteBoM(output_file, groups, net, columns.columns, pref)
    
if result:
    sys.exit(0)
else:
    sys.exit(-1)
