
import csv
import bomlib.columns as columns
from bomlib.component import *
import os, shutil
from bomlib.preferences import BomPref
from bomlib.i18n import *

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

    msg,coltitle = LangLoadStr(prefs)

    with open(filename, "w") as f:

        writer = csv.writer(f, delimiter=delimiter, lineterminator="\n")

        if not prefs.hideHeaders:
            modHeadings = []
            for i,h in enumerate(headings):
                if (h in ColumnList._COLUMNS_GEN) or (h in ColumnList._COLUMNS_PROTECTED):
                    modHeadings.append(coltitle[h])
                else:
                    modHeadings.append(h)
            if prefs.numberRows:
                writer.writerow([msg["COMPONENT"]] + modHeadings)
            else:
                writer.writerow(modHeadings)

        count = 0
        rowCount = 1

        for i, group in enumerate(groups):
            if prefs.ignoreDNF and not group.isFitted(): continue

            row = group.getRow(headings)

            if prefs.numberRows:
                row = [str(rowCount)] + row

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

            writer.writerow([msg["COMPONENT_GROUPS"]+":",nGroups])
            writer.writerow([msg["COMPONENT_COUNT_PER_PCB"]+":",nTotal])
            writer.writerow([msg["FITTED_COMPONENTS_PER_PCB"]+":", nFitted])
            writer.writerow([msg["NUMBER_OF_PCBS"]+":",prefs.boards])
            writer.writerow([msg["TOTAL_COMPONENT_COUNT"]+":", nBuild])
            writer.writerow([msg["SCHEMATIC_VERSION"]+":",net.getVersion()])
            writer.writerow([msg["SCHEMATIC_DATE"]+":",net.getSheetDate()])
            writer.writerow([msg["BOM_DATE"]+":",net.getDate()])
            writer.writerow([msg["SOURCE_FILE"]+":",net.getSource()])
            writer.writerow([msg["KICAD_VERSION"]+":",net.getTool()])

    return True
