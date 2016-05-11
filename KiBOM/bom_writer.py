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
    