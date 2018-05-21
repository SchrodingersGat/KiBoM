# _*_ coding:latin-1 _*_

import csv
import bomlib.columns as columns
from bomlib.component import *
import os, shutil
from bomlib.preferences import BomPref

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
	#override delimiter if separator specified
    if prefs.separatorCSV != None:
        delimiter = prefs.separatorCSV
    else:
        if filename.endswith(".csv"):
            delimiter = ","
        elif filename.endswith(".tsv") or filename.endswith(".txt"):
            delimiter = "\t"
        else:
            return False

    nGroups = len(groups)
    nTotal = sum([g.getCount() for g in groups])
    nFitted = sum([g.getCount() for g in groups if g.isFitted()])
    nBuild = nFitted * prefs.boards

    with open(filename, "w") as f:

        writer = csv.writer(f, delimiter=delimiter, lineterminator="\n")

        if not prefs.hideHeaders:
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
                row = [str(rowCount)] + row

            #deal with unicode characters
            #row = [el.decode('latin-1') for el in row]
            writer.writerow(row)

            try:
                count += group.getCount()
            except:
                pass

            rowCount += 1

        if not prefs.hideHeaders:
            #blank rows
            for i in range(5):
                writer.writerow([])

            writer.writerow(["Component Groups:",nGroups])
            writer.writerow(["Component Count:",nTotal])
            writer.writerow(["Fitted Components:", nFitted])
            writer.writerow(["Number of PCBs:",prefs.boards])
            writer.writerow(["Total components:", nBuild])
            writer.writerow(["Schematic Version:",net.getVersion()])
            writer.writerow(["Schematic Date:",net.getSheetDate()])
            writer.writerow(["BoM Date:",net.getDate()])
            writer.writerow(["Schematic Source:",net.getSource()])
            writer.writerow(["KiCad Version:",net.getTool()])

    return True
