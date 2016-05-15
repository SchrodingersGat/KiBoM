import columns
from component import *
from xml.etree import ElementTree
from xml.dom import minidom
from preferences import BomPref

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
        
    xml = ElementTree.Element('KiCAD_BOM', attrib = {
            'source' : net.getSource(),
            'version' : net.getVersion(),
            'date' : net.getDate(),
            'groups' : str(len(groups)),
            'components' : str(sum([group.getCount() for group in groups]))
    })
    
    for group in groups:
        if prefs.ignoreDNF and not group.isFitted():
            continue
        row = group.getRow(headings)
        
        attrib = {}
        
        for i,h in enumerate(headings):
            h = h.replace(' ','_') #replace spaces, xml no likey
            h = h.replace('"','')
            h = h.replace("'",'')
            
            attrib[h] = row[i]
            
        sub = ElementTree.SubElement(xml, "group", attrib=attrib)
    
    with open(filename,"w") as output:
        out = ElementTree.tostring(xml, 'utf-8')
        
        output.write(minidom.parseString(out).toprettyxml(indent="\t"))
        
    return True
    
