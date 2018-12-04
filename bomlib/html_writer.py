
import bomlib.columns as columns
from bomlib.component import *
import os
from bomlib.i18n import *

BG_GEN = "#E6FFEE"
BG_KICAD = "#FFE6B3"
BG_USER = "#E6F9FF"
BG_EMPTY = "#FF8080"

#return a background color for a given column title
def bgColor(col):
    #auto-generated columns
    if col in ColumnList._COLUMNS_GEN:
        return BG_GEN
    #KiCad protected columns
    elif col in ColumnList._COLUMNS_PROTECTED:
        return BG_KICAD
    #additional user columns
    else:
        return BG_USER

def link(text):

    for t in ["http","https","ftp","www"]:
        if text.startswith(t):
            return '<a href="{t}">{t}</a>'.format(t=text)

    return text

"""
Write BoM out to a HTML file
filename = path to output file (must be a .htm or .html file)
groups = [list of ComponentGroup groups]
net = netlist object
headings = [list of headings to display in the BoM file]
prefs = BomPref object
"""

def WriteHTML(filename, groups, net, headings, prefs):

    if not filename.endswith(".html") and not filename.endswith(".htm"):
        print("{fn} is not a valid html file".format(fn=filename))
        return False

    nGroups = len(groups)
    nTotal = sum([g.getCount() for g in groups])
    nFitted = sum([g.getCount() for g in groups if g.isFitted()])
    nBuild = nFitted * prefs.boards
 
    msg,coltitle = LangLoadStr(prefs)

    with open(filename,"w") as html:

        #header
        html.write("<html>\n")
        html.write("<head>\n")
        html.write('\t<meta charset="UTF-8">\n') #UTF-8 encoding for unicode support
        html.write("</head>\n")
        html.write("<body>\n")


        #PCB info
        if not prefs.hideHeaders:
            html.write("<h2>{m}</h2>\n".format(m=msg["KIBOM_PCB_BILL_OF_MATERIALS"]))
            html.write('<table border="1">\n')
            html.write("<tr><td>{m}</td><td>{source}</td></tr>\n".format(m=msg["SOURCE_FILE"],source=net.getSource()))
            html.write("<tr><td>{m}</td><td>{date}</td></tr>\n".format(m=msg["BOM_DATE"],date=net.getDate()))
            html.write("<tr><td>{m}</td><td>{version}</td></tr>\n".format(m=msg["SCHEMATIC_VERSION"],version=net.getVersion()))
            html.write("<tr><td>{m}</td><td>{date}</td></tr>\n".format(m=msg["SCHEMATIC_DATE"],date=net.getSheetDate()))
            html.write("<tr><td>{m}</td><td>{version}</td></tr>\n".format(m=msg["KICAD_VERSION"],version=net.getTool()))
            html.write("<tr><td>{m}</td><td>{n}</td></tr>\n".format(m=msg["COMPONENT_GROUPS"],n=nGroups))
            html.write("<tr><td>{m}</td><td>{n}</td></tr>\n".format(m=msg["COMPONENT_COUNT_PER_PCB"],n=nTotal))
            html.write("<tr><td>{m}</td><td>{n}</td></tr>\n".format(m=msg["FITTED_COMPONENTS_PER_PCB"],n=nFitted))
            html.write("<tr><td>{m}</td><td>{n}</td></tr>\n".format(m=msg["NUMBER_OF_PCBS"],n=prefs.boards))
            html.write("<tr><td>{m1}<br>({m2} {n} {m3})</td><td>{t}</td></tr>\n".format(m1=msg["TOTAL_COMPONENT_COUNT"],m2=msg["FOR"],m3=msg["PCBS"],n=prefs.boards, t=nBuild))
            html.write("</table>\n")
            html.write("<br>\n")
            html.write("<h2>{m}</h2>\n".format(m=msg["COMPONENT_GROUPS"]))
            html.write('<p style="background-color: {bg}">{m}</p>\n'.format(m=msg["KICAD_FIELDS_DEFAULT"],bg=BG_KICAD))
            html.write('<p style="background-color: {bg}">{m}</p>\n'.format(m=msg["GENERATED_FIELDS"],bg=BG_GEN))
            html.write('<p style="background-color: {bg}">{m}</p>\n'.format(m=msg["USER_FIELDS"],bg=BG_USER))
            html.write('<p style="background-color: {bg}">{m}</p>\n'.format(m=msg["EMPTY_FIELDS"],bg=BG_EMPTY))

        #component groups
        html.write('<table border="1">\n')

        #row titles:
        html.write("<tr>\n")
        if prefs.numberRows:
            html.write("\t<th></th>\n")
        for i,h in enumerate(headings):
            #cell background color
            bg = bgColor(h)
            if (h in ColumnList._COLUMNS_GEN) or (h in ColumnList._COLUMNS_PROTECTED):
                h = coltitle[h]
            html.write('\t<th align="center"{bg}>{h}</th>\n'.format(
                        h=h,
                        bg = ' bgcolor="{c}"'.format(c=bg) if bg else ''))
        html.write("</tr>\n")

        rowCount = 0

        for i,group in enumerate(groups):

            if prefs.ignoreDNF and not group.isFitted(): continue

            row = group.getRow(headings)

            rowCount += 1


            html.write("<tr>\n")

            if prefs.numberRows:
                html.write('\t<td align="center">{n}</td>\n'.format(n=rowCount))

            for n, r in enumerate(row):

                if len(r) == 0:
                    bg = BG_EMPTY
                else:
                    bg = bgColor(headings[n])

                html.write('\t<td align="center"{bg}>{val}</td>\n'.format(bg=' bgcolor={c}'.format(c=bg) if bg else '', val=link(r)))


            html.write("</tr>\n")

        html.write("</table>\n")
        html.write("<br><br>\n")

        html.write("</body></html>")

    return True
