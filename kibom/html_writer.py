# -*- coding: utf-8 -*-

from .component import ColumnList
from . import debug

BG_GEN = "#E6FFEE"
BG_KICAD = "#FFE6B3"
BG_USER = "#E6F9FF"
BG_EMPTY = "#FF8080"


def bgColor(col):
    """ Return a background color for a given column title """
    
    # Auto-generated columns
    if col in ColumnList._COLUMNS_GEN:
        return BG_GEN
    # KiCad protected columns
    elif col in ColumnList._COLUMNS_PROTECTED:
        return BG_KICAD
    # Additional user columns
    else:
        return BG_USER


def link(text):

    for t in ["http", "https", "ftp", "www"]:
        if text.startswith(t):
            return '<a href="{t}">{t}</a>'.format(t=text)

    return text


def WriteHTML(filename, groups, net, headings, head_names, prefs):
    """
    Write BoM out to a HTML file
    filename = path to output file (must be a .htm or .html file)
    groups = [list of ComponentGroup groups]
    net = netlist object
    headings = [list of headings to search for data in the BoM file]
    head_names = [list of headings to display in the BoM file]
    prefs = BomPref object
    """

    if not filename.endswith(".html") and not filename.endswith(".htm"):
        debug.error("{fn} is not a valid html file".format(fn=filename))
        return False

    nGroups = len(groups)
    nTotal = sum([g.getCount() for g in groups])
    nFitted = sum([g.getCount() for g in groups if g.isFitted()])
    nBuild = nFitted * prefs.boards

    link_digikey = None
    if prefs.digikey_link:
        link_digikey = prefs.digikey_link.split("\t")

    with open(filename, "w") as html:

        # HTML Header
        html.write("<html>\n")
        html.write("<head>\n")
        html.write('\t<meta charset="UTF-8">\n')  # UTF-8 encoding for unicode support
        html.write("</head>\n")
        html.write("<body>\n")

        # PCB info
        if not prefs.hideHeaders:
            html.write("<h2>KiBoM PCB Bill of Materials</h2>\n")
        if not prefs.hidePcbInfo:
            html.write('<table border="1">\n')
            html.write("<tr><td>Source File</td><td>{source}</td></tr>\n".format(source=net.getSource()))
            html.write("<tr><td>BoM Date</td><td>{date}</td></tr>\n".format(date=net.getDate()))
            html.write("<tr><td>Schematic Version</td><td>{version}</td></tr>\n".format(version=net.getVersion()))
            html.write("<tr><td>Schematic Date</td><td>{date}</td></tr>\n".format(date=net.getSheetDate()))
            html.write("<tr><td>PCB Variant</td><td>{variant}</td></tr>\n".format(variant=', '.join(prefs.pcbConfig)))
            html.write("<tr><td>KiCad Version</td><td>{version}</td></tr>\n".format(version=net.getTool()))
            html.write("<tr><td>Component Groups</td><td>{n}</td></tr>\n".format(n=nGroups))
            html.write("<tr><td>Component Count (per PCB)</td><td>{n}</td></tr>\n".format(n=nTotal))
            html.write("<tr><td>Fitted Components (per PCB)</td><td>{n}</td></tr>\n".format(n=nFitted))
            html.write("<tr><td>Number of PCBs</td><td>{n}</td></tr>\n".format(n=prefs.boards))
            html.write("<tr><td>Total Component Count<br>(for {n} PCBs)</td><td>{t}</td></tr>\n".format(n=prefs.boards, t=nBuild))
            html.write("</table>\n")
            html.write("<br>\n")

        if not prefs.hideHeaders:
            html.write("<h2>Component Groups</h2>\n")
            html.write('<p style="background-color: {bg}">KiCad Fields (default)</p>\n'.format(bg=BG_KICAD))
            html.write('<p style="background-color: {bg}">Generated Fields</p>\n'.format(bg=BG_GEN))
            html.write('<p style="background-color: {bg}">User Fields</p>\n'.format(bg=BG_USER))
            html.write('<p style="background-color: {bg}">Empty Fields</p>\n'.format(bg=BG_EMPTY))

        # Component groups
        html.write('<table border="1">\n')

        # Row titles:
        html.write("<tr>\n")
        
        if prefs.numberRows:
            html.write("\t<th></th>\n")

        for i, h in enumerate(head_names):
            # Cell background color
            bg = bgColor(headings[i])
            html.write('\t<th align="center"{bg}>{h}</th>\n'.format(
                h=h,
                bg=' bgcolor="{c}"'.format(c=bg) if bg else '')
            )

        html.write("</tr>\n")

        rowCount = 0

        for i, group in enumerate(groups):

            if prefs.ignoreDNF and not group.isFitted():
                continue

            row = group.getRow(headings)

            rowCount += 1

            html.write("<tr>\n")

            if prefs.numberRows:
                html.write('\t<td align="center">{n}</td>\n'.format(n=rowCount))

            for n, r in enumerate(row):
                if link_digikey and headings[n] in link_digikey:
                    r = '<a href="http://search.digikey.com/scripts/DkSearch/dksus.dll?Detail&name=' + r + '">' + r + '</a>'

                if (len(r) == 0) or (r.strip() == "~"):
                    bg = BG_EMPTY
                else:
                    bg = bgColor(headings[n])

                html.write('\t<td align="center"{bg}>{val}</td>\n'.format(bg=' bgcolor={c}'.format(c=bg) if bg else '', val=link(r)))

            html.write("</tr>\n")

        html.write("</table>\n")
        html.write("<br><br>\n")

        if prefs.generateDNF and rowCount != len(groups):
            html.write("<h2>Optional components (DNF=Do Not Fit)</h2>\n")
 
            # DNF component groups
            html.write('<table border="1">\n')
 
            # Row titles:
            html.write("<tr>\n")
            if prefs.numberRows:
                html.write("\t<th></th>\n")
            for i, h in enumerate(head_names):
                # Cell background color
                bg = bgColor(headings[i])
                html.write('\t<th align="center"{bg}>{h}</th>\n'.format(h=h, bg=' bgcolor="{c}"'.format(c=bg) if bg else ''))
            html.write("</tr>\n")
 
            rowCount = 0
 
            for i, group in enumerate(groups):
 
                if not(prefs.ignoreDNF and not group.isFitted()):
                    continue
 
                row = group.getRow(headings)
                rowCount += 1
                html.write("<tr>\n")
 
                if prefs.numberRows:
                    html.write('\t<td align="center">{n}</td>\n'.format(n=rowCount))
 
                for n, r in enumerate(row):
                    if link_digikey and headings[n] in link_digikey:
                        r = '<a href="http://search.digikey.com/scripts/DkSearch/dksus.dll?Detail&name=' + r + '">' + r + '</a>'

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
