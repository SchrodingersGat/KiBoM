import csv
import columns
from component import *
from xml.etree import ElementTree

import os, shutil

#make a tmp copy of a given file
def TmpFileCopy(filename):

    filename = os.path.abspath(filename)

    if os.path.exists(filename) and os.path.isfile(filename):
        shutil.copyfile(filename, filename + ".tmp")
        
def link(text):
    text = str(text)
    for t in ["http","https","ftp","www"]:
        if text.startswith(t):
            return '<a href="{t}">{t}</a>'.format(t=text)
            
    return text
        
def WriteXML(filename, groups, source, version, date, headings = columns.ColumnList._COLUMNS_ALL, ignore=[], ignoreDNF = False):
    
    filename = os.path.abspath(filename)
    
    if not filename.endswith(".xml"):
        return False
        
    headings = [h for h in headings if h not in ignore]
        
    try:
        TmpFileCopy(filename)
            
        xml = ElementTree.Element('"KiCAD Bom"', attrib = {
                '"source"' : source,
                '"version"' : version,
                '"date"' : date,
                '"groups"' : str(len(groups)),
                '"components"' : str(sum([group.getCount() for group in groups]))
        })
        
        for group in groups:
            row = group.getKicadRow(headings)
            
            attrib = {}
            
            for i,h in enumerate(headings):
                attrib['"' + h + '"'] = row[i]
                
            sub = ElementTree.SubElement(xml, "group", attrib=attrib)
        
        #write the document
        tree = ElementTree.ElementTree(xml)
        
        tree.write(filename)
            
        return True
        
    except BaseException as e:
        print(str(e))
        return False
        
    return True
    
def WriteHTML(filename, groups, net, headings = columns.ColumnList._COLUMNS_ALL, ignore=[], ignoreDNF=False, numberRows=True):

    filename = os.path.abspath(filename)
    
    headings = [h for h in headings if not h in ignore]
    
    try:
        TmpFileCopy(filename)
        
        with open(filename,"w") as html:
            
            #header
            html.write("<html>\n")
            html.write("<body>\n")
            
            #PCB info
            html.write("<h2>PCB Information</h2>\n")
            html.write("<br>Source File: {source}\n".format(source=net.getSource()))
            html.write("<br>Date: {date}\n".format(date=net.getDate()))
            html.write("<br>Version: {version}\n".format(version=net.getVersion()))
            html.write("<br>\n")
            html.write("<h2>Component Groups</h2>\n")
            
            #component groups
            html.write('<table border="1">\n')
            
            #row titles:
            html.write("<tr>\n")
            if numberRows:
                html.write("\t<th></th>\n")
            for h in headings:
                html.write("\t<th>{h}</th>\n".format(h=h))
            html.write("</tr>\n")
            
            rowCount = 0
            
            for i,group in enumerate(groups):
            
                if ignoreDNF and not group.isFitted(): continue
                
                row = group.getKicadRow(headings)
                
                rowCount += 1
                
                if numberRows:
                    row = [rowCount] + row
                    
                html.write("<tr>\n")
                
                for r in row:
                    html.write("\t<td>{val}</td>\n".format(val=link(r)))
                    
            
                html.write("</tr>\n")
                
            html.write("</table>\n")
            
            html.write("</body></html>")
            
            
    except BaseException as e:
        print(str(e))
        return False
        
    return True
    
        
        

def WriteCSV(filename, groups, source, version, date, headings = columns.ColumnList._COLUMNS_ALL, ignore=[], ignoreDNF=False, numberRows=True):
    
    filename = os.path.abspath(filename)
    
    #delimeter is assumed from file extension
    if filename.endswith(".csv"):
        delimiter = ","
    elif filename.endswith(".tsv") or filename.endswith(".txt"):
        delimiter = "\t"
    else:
        return False
        
    headings = [h for h in headings if h not in ignore] #copy across the headings
    
    try:
        #make a copy of the file
        TmpFileCopy(filename)
        
        with open(filename, "w") as f:
        
            writer = csv.writer(f, delimiter=delimiter, lineterminator="\n")
            
            if numberRows:
                writer.writerow(["Component"] + headings)
            else:
                writer.writerow(headings)
                
            count = 0
            rowCount = 1
            
            for i, group in enumerate(groups):
                if ignoreDNF and not group.isFitted(): continue
                
                row = group.getKicadRow(headings)
                
                if numberRows:
                    row = [rowCount] + row
                    
                writer.writerow(row)
                
                try:
                    count += group.getCount()
                except:
                    pass
                    
                rowCount += 1
                
            #blank rows
            for i in range(5):
                writer.writerow([])
                
            writer.writerow(["Component Count:",componentCount])
            writer.writerow(["Component Groups:",len(groups)])
            writer.writerow(["Source:",source])
            writer.writerow(["Version:",version])
            writer.writerow(["Date:",date])
            
        return True
 
 
    except BaseException as e:
        print(str(e))
        return False
        
    return True
    