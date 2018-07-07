
import bomlib.columns as columns
from bomlib.component import *
import os

BG_GEN = "#E6FFEE"
BG_KICAD = "#FFE6B3"
BG_USER = "#E6F9FF"
BG_EMPTY = "#FF8080"

#todo: remove
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
            return '<a href="{t}" target="_blank">{t}</a>'.format(t=text)

    return text

"""
Write BoM out to a HTML file
filename = path to output file (must be a .htm or .html file)
groups = [list of ComponentGroup groups]
net = netlist object
headings = [list of headings to display in the BoM file]
prefs = BomPref object
"""
#writes out a flatter, more modern looking table design.
def HTMLPretty(filename, groups, net, headings, prefs):

    if not filename.endswith(".html") and not filename.endswith(".htm"):
        print("{fn} is not a valid html file".format(fn=filename))
        return False

    nGroups = len(groups)
    nTotal = sum([g.getCount() for g in groups])
    nFitted = sum([g.getCount() for g in groups if g.isFitted()])
    nBuild = nFitted * prefs.boards

    with open(filename,"w") as html:      
        html.write("<html>\n")
        html.write("<head>\n")
        html.write('\t<meta charset="UTF-8">\n') #UTF-8 encoding for unicode support
        html.write('<link rel="stylesheet" type="text/css" href="http://xtian.nvg.org/prettyhtml/bom.css" />\n')
        html.write("</head>\n")
        html.write("<body>\n")

        html.write('<div class="header">\n')
        html.write('<div class="titlebox">\n')
        html.write("<p><h1>Bill of Materials</h1></P>\n")
        if prefs.authorname != "":
            html.write('<p style="padding-left: 25px; margin-top: -20px;"><input type="text" style="font-size:1.5em; width:100%;" value="{title_of_project}"></p>\n'.format(title_of_project=prefs.titleofproject))
        else:
            html.write('<p style="padding-left: 25px; margin-top: -20px;"><input type="text" onfocus="this.value=\'\'" style="font-size:1.5em; width:100%;" value="Skriv inn tittel her"></p>\n')
        if prefs.titleofproject != "":
            html.write('<p style="padding-left: 25px; margin-top: -20px;"><input type="text" style="font-size:1.5em; width:100%;" value="{author_of_project}"></p>\n'.format(author_of_project=prefs.authorname))
        else:
            html.write('<p style="padding-left: 25px; margin-top: -20px;"><input type="text" onfocus="this.value=\'\'" style="font-size:1em; width:100%; font-style: italic;" value="Skriv inn ditt navn her"></p>\n')
        html.write("</div>\n")
        html.write('<div class="logobox">\n')
        print(prefs.image)
        if prefs.image != "":
            html.write('<img src="{logo}">\n'.format(logo=prefs.image))
        else:
            #todo:
            #fix an actual logo host
            html.write('<img src="https://blogdotoshparkdotcom.files.wordpress.com/2016/12/screenshot-from-2016-12-21-20-26-05.png">\n')
        html.write("</div>\n")
        html.write("</div>\n")    

        #component groups
        html.write('<table class="minimalistBlack">\n')

        #row titles:
        html.write("<thead>\n")
        html.write("<tr>\n")
        if prefs.numberRows:
            html.write("\t<th></th>\n")
        for i,h in enumerate(headings):
            #cell background color
            bg = 0xffffff;
            html.write('\t<th align="center">{h}</th>\n'.format(
                        h=h))
        html.write("</tr>\n")
        html.write("</thead>\n")
        rowCount = 0

        for i,group in enumerate(groups):

            if prefs.ignoreDNF and not group.isFitted(): continue

            row = group.getRow(headings)

            rowCount += 1


            html.write("<tbody>\n")
            html.write("<tr>\n")

            if prefs.numberRows:
                html.write('\t<td align="center">{n}</td>\n'.format(n=rowCount))

            for n, r in enumerate(row):

                if len(r) == 0:
                    bg = BG_EMPTY
                else:
                    bg = bgColor(headings[n])

                html.write('\t<td align="left">{val}</td>\n'.format(bg=' bgcolor={c}', val=link(r)))
                
            html.write("</tr>\n")
            html.write("</tbody>\n")

        html.write("</table>\n")
        html.write("<br><br>\n")

        html.write("</body></html>")

    return True
