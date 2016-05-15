from __future__ import print_function

import re
import csv
import sys
import os
import shutil

here = os.path.abspath(os.path.dirname(sys.argv[0]))

sys.path.append(here)

from KiBOM.columns import ColumnList
from KiBOM.netlist_reader import *
from KiBOM.bom_writer import *
from KiBOM.preferences import BomPref

def close(*arg):
    print(*arg)
    sys.exit(0)
    
if len(sys.argv) < 2:
    close("No input file supplied")
    
input_file = sys.argv[1].replace("\\",os.path.sep).replace("/",os.path.sep)

input_file = os.path.abspath(input_file)
    
if not input_file.endswith(".xml"):
    close("Supplied file is not .xml")

#work out an output file
ext = ".csv"

if len(sys.argv) < 3:
    #no output file supplied, assume .csv
    output_file = input_file.replace(".xml",".csv")
else:
    output_file = sys.argv[2].replace("\\",os.path.sep).replace("/",os.path.sep)
    
    valid = False
    
    for e in [".xml",".csv",".txt",".tsv",".html"]:
        if output_file.endswith(e):
            valid = True
            ext = e
            break
    if not valid:
        output_file += ext
        
    output_file = os.path.abspath(output_file)
    
print("Input File: " + input_file)
print("Output File: " + output_file)

#preferences
ignore = []
ignoreDNF = False
numberRows = True

#Look for a '.bom' preference file
pref_file = os.path.join(os.path.dirname(input_file) , ".bom")

#read preferences from file. If file does not exists, default preferences will be used
pref = BomPref()
pref.Read(pref_file, verbose=True)

#write preference file back out (first run will generate a file with default preferences)
pref.Write(pref_file)

#individual components
components = []

#component groups
groups = []

#read out the netlist
net = netlist(input_file)

#extract the components
components = net.getInterestingComponents()

#group the components
groups = net.groupComponents(components)

columns = ColumnList()

#read out all available fields
for g in groups:
    for f in g.fields:
        columns.AddColumn(f)

#Finally, write the BoM out to file
result = WriteBoM(output_file, groups, net, columns.columns, pref)
    
if result:
    sys.exit(0)
else:
    sys.exit(-1)
