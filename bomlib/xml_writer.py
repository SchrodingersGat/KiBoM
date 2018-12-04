import bomlib.columns as columns
from bomlib.component import *
from xml.etree import ElementTree
from xml.dom import minidom
from bomlib.preferences import BomPref
from bomlib.i18n import *

"""
Write BoM out to an XML file
filename = path to output file (must be a .xml)
groups = [list of ComponentGroup groups]
net = netlist object
headings = [list of headings to display in the BoM file]
prefs = BomPref object
"""

def WriteXML(filename, groups, net, headings, prefs):

    if not filename.endswith(".xml"):
        return False

    nGroups = len(groups)
    nTotal = sum([g.getCount() for g in groups])
    nFitted = sum([g.getCount() for g in groups if g.isFitted()])
    nBuild = nFitted * prefs.boards
    
    msg,coltitle = LangLoadStr(prefs)

    for key in msg:
        msg[key] = msg[key].replace(' ','_') #replace spaces, xml no likey
        msg[key] = msg[key].replace('"','')
        msg[key] = msg[key].replace("'",'')
        msg[key] = msg[key].replace("/",'_')
        msg[key] = msg[key].replace("(",'')
        msg[key] = msg[key].replace(")",'')
        msg[key] = msg[key].decode('utf-8')

    attrib = {}

    attrib[msg["SOURCE_FILE"]] = net.getSource()
    attrib[msg["SCHEMATIC_VERSION"]] = net.getVersion()
    attrib[msg["SCHEMATIC_DATE"]] = net.getSheetDate()
    attrib[msg["BOM_DATE"]] = net.getDate()
    attrib[msg["KICAD_VERSION"]] = net.getTool()
    attrib[msg["COMPONENT_GROUPS"]] = str(nGroups)
    attrib[msg["COMPONENT_COUNT_PER_PCB"]] = str(nTotal)
    attrib[msg["FITTED_COMPONENTS_PER_PCB"]] = str(nFitted)

    attrib[msg["NUMBER_OF_PCBS"]] = str(prefs.boards)
    attrib[msg["TOTAL_COMPONENT_COUNT"]] = str(nBuild)

    xml = ElementTree.Element('KiCad_BOM', attrib = attrib, encoding='utf-8')

    for group in groups:
        if prefs.ignoreDNF and not group.isFitted():
            continue

        row = group.getRow(headings)

        attrib = {}

        for i,h in enumerate(headings):
            if (h in ColumnList._COLUMNS_GEN) or (h in ColumnList._COLUMNS_PROTECTED):
                h = coltitle[h]
            h = h.replace(' ','_') #replace spaces, xml no likey
            h = h.replace('"','')
            h = h.replace("'",'')
            h = h.replace("/",'_')
            h = h.replace("(",'')
            h = h.replace(")",'')
            h = h.decode('utf-8')

            attrib[h] = str(row[i]).decode('utf-8',errors='ignore')

        sub = ElementTree.SubElement(xml, "group", attrib=attrib)

    with open(filename,"w") as output:
        out = ElementTree.tostring(xml, encoding="utf-8")
        unistr = minidom.parseString(out).toprettyxml(indent="\t").replace(u'<?xml version="1.0" ?>',
                          u'<?xml version="1.0" encoding="utf-8"?>')
        out = unistr.encode('utf-8', 'xmlcharrefreplace')
        output.write(out)

    return True
