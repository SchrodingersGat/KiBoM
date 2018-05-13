import xlsxwriter
import bomlib.columns as columns
from bomlib.component import *
import os, shutil
from bomlib.preferences import BomPref

"""
Write BoM out to an XLSX file
filename = path to output file (must be an .xlsx file)
groups = [list of ComponentGroup groups]
net = netlist object
headings = [list of headings to display in the BoM file]
prefs = BomPref object
"""

def WriteXLSX(filename, groups, net, headings, prefs):

    filename = os.path.abspath(filename)

    nGroups = len(groups)
    nTotal = sum([g.getCount() for g in groups])
    nFitted = sum([g.getCount() for g in groups if g.isFitted()])
    nBuild = nFitted * prefs.boards


    with xlsxwriter.Workbook(filename, {"in_memory": True}) as workbook:
        # Starting row
        cur_row = 0

        # Add a worksheet called BOM
        worksheet = workbook.add_worksheet("BOM")

        # Formatting
        bold = workbook.add_format({'bold': True})

        # Only add headers if enabled
        if not prefs.hideHeaders:
            # Add numbered rows if enabled
            if prefs.numberRows:
                worksheet.write_row(cur_row, 0, ["Component"] + headings, bold)
            else:
                worksheet.write_row(cur_row, 0, headings, bold)
            cur_row += 1

        # Give the columns more space (autosize would have to be computed)
        worksheet.set_column(0, len(headings) + 1, 20)

        # Add each of the groups to the worksheet as a line-item
        for i, group in enumerate(groups):
            # Skip ignored fields
            if prefs.ignoreDNF and not group.isFitted():
                continue

            # Retrieve row fields
            row = group.getRow(headings)

            # Add a line-item number if specified
            if prefs.numberRows:
                row = [str(cur_row)] + row

            #deal with unicode characters
            #row = [el.decode('latin-1') for el in row]
            # Write each column, attempt to convert numbers before writing
            for index, item in enumerate(row):
                try:
                    newint = int(item, 10)
                    row[index] = newint
                except:
                    pass
                worksheet.write(cur_row, index, row[index])

            # Increment row
            cur_row += 1

        if not prefs.hideHeaders:
            # Blank rows, skip 5 rows
            cur_row += 5

            # Add BOM information
            bom_info = [
                ["Component Groups:", nGroups],
                ["Component Count:", nTotal],
                ["Fitted Components:", nFitted],
                ["Number of PCBs:", prefs.boards],
                ["Total components:", nBuild],
                ["Schematic Version:", net.getVersion()],
                ["Schematic Date:", net.getSheetDate()],
                ["BoM Date:", net.getDate()],
                ["BoM Date:", net.getDate()],
                ["KiCad Version:", net.getTool()],
            ]
            for group in bom_info:
                worksheet.write(cur_row, 0, group[0], bold)
                worksheet.write(cur_row, 1, group[1])
                cur_row += 1

    return True
