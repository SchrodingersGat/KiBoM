import csv
import columns
from component import *
import os, shutil
from preferences import BomPref

"""
Write BoM out to a CSV file
filename = path to output file (must be a .csv, .txt or .tsv file)
groups = [list of ComponentGroup groups]
net = netlist object
headings = [list of headings to display in the BoM file]
prefs = BomPref object
"""

def WriteCSV(filename, groups, net, headings, prefs):
    
    filename = os.path.abspath(filename)
    
    #delimeter is assumed from file extension
    if filename.endswith(".csv"):
        delimiter = ","
    elif filename.endswith(".tsv") or filename.endswith(".txt"):
        delimiter = "\t"
    else:
        return False
        
    with open(filename, "w") as f:
    
        writer = csv.writer(f, delimiter=delimiter, lineterminator="\n")
        
        if prefs.numberRows:
            writer.writerow(["Component"] + headings)
        else:
            writer.writerow(headings)
            
        count = 0
        rowCount = 1
        
        for i, group in enumerate(groups):
            if prefs.ignoreDNF and not group.isFitted(): continue
            
            row = group.getRow(headings)
            
            if prefs.numberRows:
                row = [rowCount] + row
                
            writer.writerow(row)
            
            try:
                count += group.getCount()
            except:
                pass
                
            rowCount += 1
            
        #blank rows
        for i in range(5):
            writer.writerow([])
            
        writer.writerow(["Component Count:",sum([g.getCount() for g in groups])])
        writer.writerow(["Component Groups:",len(groups)])
        writer.writerow(["Source:",net.getSource()])
        writer.writerow(["Version:",net.getVersion()])
        writer.writerow(["Date:",net.getDate()])
        
    return True