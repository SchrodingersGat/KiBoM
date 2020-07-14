"""
Write BoM out to an XML file
filename = path to output file (must be a .xml)
groups = [list of ComponentGroup groups]
net = netlist object
headings = [list of headings to display in the BoM file]
prefs = BomPref object
"""

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from xml.etree import ElementTree
from xml.dom import minidom


def WriteXML(filename, groups, net, headings, prefs):

    if not filename.endswith(".xml"):
        return False

    nGroups = len(groups)
    nTotal = sum([g.getCount() for g in groups])
    nFitted = sum([g.getCount() for g in groups if g.isFitted()])
    nBuild = nFitted * prefs.boards

    attrib = {}

    attrib['Schematic_Source'] = net.getSource()
    attrib['Schematic_Version'] = net.getVersion()
    attrib['Schematic_Date'] = net.getSheetDate()
    attrib['PCB_Variant'] = ', '.join(prefs.pcbConfig)
    attrib['BOM_Date'] = net.getDate()
    attrib['KiCad_Version'] = net.getTool()
    attrib['Component_Groups'] = str(nGroups)
    attrib['Component_Count'] = str(nTotal)
    attrib['Fitted_Components'] = str(nFitted)

    attrib['Number_of_PCBs'] = str(prefs.boards)
    attrib['Total_Components'] = str(nBuild)

    xml = ElementTree.Element('KiCad_BOM', attrib=attrib, encoding='utf-8')

    for group in groups:
        if prefs.ignoreDNF and not group.isFitted():
            continue

        row = group.getRow(headings)

        attrib = {}

        for i, h in enumerate(headings):
            h = h.replace(' ', '_')  # Replace spaces, xml no likey
            h = h.replace('"', '')
            h = h.replace("'", '')

            attrib[h] = str(row[i])

        # sub = ElementTree.SubElement(xml, "group", attrib=attrib)

    with open(filename, "w") as output:
        out = ElementTree.tostring(xml, encoding="utf-8")
        output.write(minidom.parseString(out).toprettyxml(indent="\t"))

    return True
