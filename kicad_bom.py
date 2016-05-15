
from __future__ import print_function

import re
import csv
import sys
import os
import shutil

DELIMITER = ","

here = os.path.abspath(os.path.dirname(sys.argv[0]))

sys.path.append(here)

from KiBOM.columns import ColumnList
from KiBOM.netlist_reader import *
from KiBOM.bom_writer import *

#import bomfunk_netlist_reader
#import bomfunk_csv
#from bomfunk_csv import CSV_DEFAULT as COLUMNS

global DEBUG
DEBUG = True

def debug(msg):
    global DEBUG
    if DEBUG == True:
        print(msg)

def close(*arg):
    print(*arg)
    sys.exit(0)

def error(*arg):
    print(*arg)
    sys.exit(-1)
    
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

if ext in [".csv",".tsv",".txt"]:
    if WriteCSV(output_file, groups, net.getSource(), net.getVersion(), net.getDate()):
        print("Success! Wrote components to " + output_file)
    else:
        print("Error writing to " + output_file)
        
elif ext == ".xml":
    WriteXML(output_file, groups, net.getSource(), net.getVersion(), net.getDate())

elif ext in ['.htm','.html']:
    WriteHTML(output_file, groups, net)
    
