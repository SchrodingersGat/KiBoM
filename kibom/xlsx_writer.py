# _*_ coding:latin-1 _*_

try:
    import xlsxwriter
except:
    def WriteXLSX(filename, groups, net, headings, head_names, prefs):
        return False
else:
    import os

    """
    Write BoM out to a XLSX file
    filename = path to output file (must be a .xlsx file)
    groups = [list of ComponentGroup groups]
    net = netlist object
    headings = [list of headings to search for data in the BoM file]
    head_names = [list of headings to display in the BoM file]
    prefs = BomPref object
    """

    def WriteXLSX(filename, groups, net, headings, head_names, prefs):

        filename = os.path.abspath(filename)

        if not filename.endswith(".xlsx"):
            return False

        nGroups = len(groups)
        nTotal = sum([g.getCount() for g in groups])
        nFitted = sum([g.getCount() for g in groups if g.isFitted()])
        nBuild = nFitted * prefs.boards

        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()

        if prefs.numberRows:
            comp = "Component"
            if comp.lower() in prefs.colRename:
                comp = prefs.colRename[comp.lower()]
            row_headings = [comp] + head_names
        else:
            row_headings = head_names

        link_datasheet = prefs.as_link
        link_digikey = None
        if prefs.digikey_link:
            link_digikey = prefs.digikey_link.split("\t")

        cellformats = {}
        column_widths = {}
        for i in range(len(row_headings)):
            cellformats[i] = workbook.add_format({'align': 'center_across'})
            column_widths[i] = len(row_headings[i]) + 10

            if not prefs.hideHeaders:
                worksheet.write_string(0, i, row_headings[i], cellformats[i])

        count = 0
        rowCount = 1

        for i, group in enumerate(groups):
            if prefs.ignoreDNF and not group.isFitted():
                continue

            row = group.getRow(headings)

            if prefs.numberRows:
                row = [str(rowCount)] + row

            for columnCount in range(len(row)):
                
                cell = row[columnCount]
                if link_datasheet and headings[columnCount - 1] == link_datasheet:
                    worksheet.write_url(rowCount, columnCount, cell, cellformats[columnCount])
                elif link_digikey and headings[columnCount - 1] in link_digikey:
                    url = "https://www.digikey.com/en/products?mpart=" + cell
                    worksheet.write_url(rowCount, columnCount, url, cellformats[columnCount], cell)
                else:
                    worksheet.write_string(rowCount, columnCount, cell, cellformats[columnCount])

                if len(cell) > column_widths[columnCount] - 5:
                    column_widths[columnCount] = len(cell) + 5

            try:
                count += group.getCount()
            except:
                pass
                
            rowCount += 1

        if not prefs.hidePcbInfo:
            # Add a few blank rows
            for i in range(5):
                rowCount += 1

            cellformat_left = workbook.add_format({'align': 'left'})

            worksheet.write_string(rowCount, 0, "Component Groups:", cellformats[0])
            worksheet.write_number(rowCount, 1, nGroups, cellformat_left)
            rowCount += 1

            worksheet.write_string(rowCount, 0, "Component Count:", cellformats[0])
            worksheet.write_number(rowCount, 1, nTotal, cellformat_left)
            rowCount += 1

            worksheet.write_string(rowCount, 0, "Fitted Components:", cellformats[0])
            worksheet.write_number(rowCount, 1, nFitted, cellformat_left)
            rowCount += 1

            worksheet.write_string(rowCount, 0, "Number of PCBs:", cellformats[0])
            worksheet.write_number(rowCount, 1, prefs.boards, cellformat_left)
            rowCount += 1

            worksheet.write_string(rowCount, 0, "Total components:", cellformats[0])
            worksheet.write_number(rowCount, 1, nBuild, cellformat_left)
            rowCount += 1

            worksheet.write_string(rowCount, 0, "Schematic Version:", cellformats[0])
            worksheet.write_string(rowCount, 1, net.getVersion(), cellformat_left)
            rowCount += 1

            if len(net.getVersion()) > column_widths[1]:
                column_widths[1] = len(net.getVersion())

            worksheet.write_string(rowCount, 0, "Schematic Date:", cellformats[0])
            worksheet.write_string(rowCount, 1, net.getSheetDate(), cellformat_left)
            rowCount += 1

            if len(net.getSheetDate()) > column_widths[1]:
                column_widths[1] = len(net.getSheetDate())

            worksheet.write_string(rowCount, 0, "BoM Date:", cellformats[0])
            worksheet.write_string(rowCount, 1, net.getDate(), cellformat_left)
            rowCount += 1

            if len(net.getDate()) > column_widths[1]:
                column_widths[1] = len(net.getDate())

            worksheet.write_string(rowCount, 0, "Schematic Source:", cellformats[0])
            worksheet.write_string(rowCount, 1, net.getSource(), cellformat_left)
            rowCount += 1

            if len(net.getSource()) > column_widths[1]:
                column_widths[1] = len(net.getSource())

            worksheet.write_string(rowCount, 0, "KiCad Version:", cellformats[0])
            worksheet.write_string(rowCount, 1, net.getTool(), cellformat_left)
            rowCount += 1

            if len(net.getTool()) > column_widths[1]:
                column_widths[1] = len(net.getTool())

        for i in range(len(column_widths)):
            worksheet.set_column(i, i, column_widths[i])

        workbook.close()

        return True
