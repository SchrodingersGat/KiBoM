
import bomlib.columns as columns
from bomlib.component import *
import os

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

    with open(filename,"w") as html:

        #header
        html.write("<html>\n")
        html.write("<head>\n")
        html.write('\t<meta charset="UTF-8">\n') #UTF-8 encoding for unicode support
        html.write("</head>\n")
        html.write("<body>\n")


        #PCB info
        if not prefs.hideHeaders:
            html.write("<h2>KiBoM PCB Bill of Materials</h2>\n")
            html.write('<table border="1">\n')
            html.write("<tr><td>Source File</td><td>{source}</td></tr>\n".format(source=net.getSource()))
            html.write("<tr><td>BoM Date</td><td>{date}</td></tr>\n".format(date=net.getDate()))
            html.write("<tr><td>Schematic Version</td><td>{version}</td></tr>\n".format(version=net.getVersion()))
            html.write("<tr><td>Schematic Date</td><td>{date}</td></tr>\n".format(date=net.getSheetDate()))
            html.write("<tr><td>KiCad Version</td><td>{version}</td></tr>\n".format(version=net.getTool()))
            html.write("<tr><td>Component Groups</td><td>{n}</td></tr>\n".format(n=nGroups))
            html.write("<tr><td>Component Count (per PCB)</td><td>{n}</td></tr>\n".format(n=nTotal))
            html.write("<tr><td>Fitted Components (per PCB)</td><td>{n}</td></tr>\n".format(n=nFitted))
            html.write("<tr><td>Number of PCBs</td><td>{n}</td></tr>\n".format(n=prefs.boards))
            html.write("<tr><td>Total Component Count<br>(for {n} PCBs)</td><td>{t}</td></tr>\n".format(n=prefs.boards, t=nBuild))
            html.write("</table>\n")
            html.write("<br>\n")
            html.write("<h2>Component Groups</h2>\n")
            html.write('<p style="background-color: {bg}">KiCad Fields (default)</p>\n'.format(bg=BG_KICAD))
            html.write('<p style="background-color: {bg}">Generated Fields</p>\n'.format(bg=BG_GEN))
            html.write('<p style="background-color: {bg}">User Fields</p>\n'.format(bg=BG_USER))
            html.write('<p style="background-color: {bg}">Empty Fields</p>\n'.format(bg=BG_EMPTY))

        #component groups
        html.write('<table border="1">\n')

        #row titles:
        html.write("<tr>\n")
        if prefs.numberRows:
            html.write("\t<th></th>\n")
        for i,h in enumerate(headings):
            #cell background color
            bg = bgColor(h)
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
