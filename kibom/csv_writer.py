# _*_ coding:latin-1 _*_

import csv
import os
import sys


def WriteCSV(filename, groups, net, headings, prefs):
    """
    Write BoM out to a CSV file
    filename = path to output file (must be a .csv, .txt or .tsv file)
    groups = [list of ComponentGroup groups]
    net = netlist object
    headings = [list of headings to display in the BoM file]
    prefs = BomPref object
    """

    filename = os.path.abspath(filename)

    # Delimeter is assumed from file extension
    # Override delimiter if separator specified
    if prefs.separatorCSV is not None:
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

    if (sys.version_info[0] >= 3):
        f = open(filename, "w", encoding='utf-8')
    else:
        f = open(filename, "w")

    writer = csv.writer(f, delimiter=delimiter, lineterminator="\n")

    if not prefs.hideHeaders:
        if prefs.numberRows:
            writer.writerow(["Component"] + headings)
        else:
            writer.writerow(headings)

    count = 0
    rowCount = 1

    for group in groups:
        if prefs.ignoreDNF and not group.isFitted():
            continue

        row = group.getRow(headings)

        if prefs.numberRows:
            row = [str(rowCount)] + row

        # Deal with unicode characters
        # Row = [el.decode('latin-1') for el in row]
        writer.writerow(row)

        try:
            count += group.getCount()
        except:
            pass

        rowCount += 1

    if not prefs.hidePcbInfo:
        # Add some blank rows
        for i in range(5):
            writer.writerow([])

        writer.writerow(["Component Groups:", nGroups])
        writer.writerow(["Component Count:", nTotal])
        writer.writerow(["Fitted Components:", nFitted])
        writer.writerow(["Number of PCBs:", prefs.boards])
        writer.writerow(["Total components:", nBuild])
        writer.writerow(["Schematic Version:", net.getVersion()])
        writer.writerow(["Schematic Date:", net.getSheetDate()])
        writer.writerow(["PCB Variant:", ' + '.join(prefs.pcbConfig)])
        writer.writerow(["BoM Date:", net.getDate()])
        writer.writerow(["Schematic Source:", net.getSource()])
        writer.writerow(["KiCad Version:", net.getTool()])

    f.close()

    return True
