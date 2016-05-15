from columns import ColumnList, Column

import units

from sort import natural_sort

DNF = ["dnf", "do not fit", "nofit", "no stuff", "nostuff", "noload", "do not load"]

class Component():
    """Class for a component, aka 'comp' in the xml netlist file.
    This component class is implemented by wrapping an xmlElement instance
    with accessors.  The xmlElement is held in field 'element'.
    """

    def __init__(self, xml_element):
        self.element = xml_element
        self.libpart = None

        # Set to true when this component is included in a component group
        self.grouped = False

    #compare the value of this part, to the value of another part (see if they match)
    def compareValue(self, other):
        #simple string comparison
        if self.getValue().lower() == other.getValue().lower(): return True

        #otherwise, perform a more complicated value comparison
        if units.compareValues(self.getValue(), other.getValue()): return True

        #no match, return False
        return False

    #compare footprint with another component
    def compareFootprint(self, other):
        return self.getFootprint().lower() == other.getFootprint().lower()

    #compare the component library of this part to another part
    def compareLibName(self, other):
        return self.getLibName().lower() == other.getLibName().lower()

    #determine if two parts have the same name
    def comparePartName(self, other):
        pn1 = self.getPartName().lower()
        pn2 = other.getPartName().lower()

        #simple direct match
        if pn1 == pn2: return True

        #compare part aliases e.g. "c" to "c_small"
        for alias in ALIASES:
            if pn1 in alias and pn2 in alias:
                return True

        return False

    #Equivalency operator is used to determine if two parts are 'equal'
    def __eq__(self, other):
        """Equlivalency operator, remember this can be easily overloaded"""

        #special case for connectors, as the "Value" is the description of the connector (and is somewhat meaningless)
        if "connector" in self.getDescription().lower():
            #ignore "value"
            valueResult = True
        else:
            valueResult = self.compareValue(other)

        return valueResult and self.compareFootprint(other) and self.compareLibName(other) and self.comparePartName(other) and self.isFitted() == other.isFitted()

    def setLibPart(self, part):
        self.libpart = part

    def getPrefix(self): #return the reference prefix
        #e.g. if this component has a reference U12, will return "U"
        prefix = ""

        for c in self.getRef():
            if c.isalpha(): prefix += c
            else: break

        return prefix

    def getLibPart(self):
        return self.libpart

    def getPartName(self):
        return self.element.get("libsource", "part")

    def getLibName(self):
        return self.element.get("libsource", "lib")

    def setValue(self, value):
        """Set the value of this component"""
        v = self.element.getChild("value")
        if v:
            v.setChars(value)

    def getValue(self):
        return self.element.get("value")

    def getField(self, name, libraryToo=True):
        """Return the value of a field named name. The component is first
        checked for the field, and then the components library part is checked
        for the field. If the field doesn't exist in either, an empty string is
        returned

        Keywords:
        name -- The name of the field to return the value for
        libraryToo --   look in the libpart's fields for the same name if not found
                        in component itself
        """

        field = self.element.get("field", "name", name)
        if field == "" and libraryToo:
            field = self.libpart.getField(name)
        return field

    def getFieldNames(self):
        """Return a list of field names in play for this component.  Mandatory
        fields are not included, and they are: Value, Footprint, Datasheet, Ref.
        The netlist format only includes fields with non-empty values.  So if a field
        is empty, it will not be present in the returned list.
        """
        fieldNames = []
        fields = self.element.getChild('fields')
        if fields:
            for f in fields.getChildren():
                fieldNames.append( f.get('field','name') )
        return fieldNames

    def getRef(self):
        return self.element.get("comp", "ref")

    #determine if a component is FITTED or not
    def isFitted(self):

        check = [self.getValue().lower(), self.getField("Notes").lower()]

        for item in check:
            if any([dnf in item for dnf in DNF]): return False

        return True

    def getFootprint(self, libraryToo=True):
        ret = self.element.get("footprint")
        if ret =="" and libraryToo:
            ret = self.libpart.getFootprint()
        return ret

    def getDatasheet(self, libraryToo=True):
        return self.libpart.getDatasheet()

    def getTimestamp(self):
        return self.element.get("tstamp")

    def getDescription(self):
        return self.libpart.getDescription()

class ComponentGroup():

    """
    Initialize the group with no components, and default fields
    """
    def __init__(self):
        self.components = []
        self.fields = dict.fromkeys(ColumnList._COLUMNS_GROUPED)    #columns loaded from KiCAD
        self.csvFields = dict.fromkeys(ColumnList._COLUMNS_GROUPED) #columns loaded from .csv file
        
    def getField(self, field):
        if not field in self.fields.keys(): return ""
        if not self.fields[field]: return ""
        return str(self.fields[field])
        
    def getCSVField(self, field):
    
        #ignore protected fields
        if field in CSV_PROTECTED: return ""
    
        if not field in self.csvFields.keys(): return ""
        if not self.csvFields[field]: return ""
        return str(self.csvFields[field])

    def getHarmonizedField(self,field):
    
        #for protected fields, source from KiCAD
        if field in CSV_PROTECTED:
            return self.getField(field)

        #if there is kicad data, that takes preference
        if not self.getField(field) == "":
            return self.getField(field)

        elif not self.getCSVField(field) == "":
            return self.getCSVField(field)
        else:
            return ""
        
        
    def compareCSVLine(self, line):
        """
        Compare a line (dict) and see if it matches this component group
        """
        for field in CSV_MATCH:
            if not field in line.keys(): return False
            if not field in self.fields.keys(): return False
            if not line[field] == self.fields[field]: return False
            
        return True
        
    def getCount(self):
        for c in self.components:
            if not c.isFitted(): return "0"
        return len(self.components)

    #Test if a given component fits in this group
    def matchComponent(self, c):
        if len(self.components) == 0: return True
        if c == self.components[0]: return True

    #test if a given component is already contained in this grop
    def containsComponent(self, c):
        if self.matchComponent(c) == False: return False
        
        for comp in self.components:
            if comp.getRef() == c.getRef(): return True
            
        return False

    #add a component to the group
    def addComponent(self, c):
    
        if len(self.components) == 0:
            self.components.append(c)
        elif self.containsComponent(c):
            return
        elif self.matchComponent(c):
            self.components.append(c)

    def isFitted(self):
        return any([c.isFitted() for c in self.components])

    #return a list of the components
    def getRefs(self):
        #print([c.getRef() for c in self.components]))
        #return " ".join([c.getRef() for c in self.components]) 
        return " ".join([c.getRef() for c in self.components])

    #sort the components in correct order
    def sortComponents(self):
        self.components = sorted(self.components, key=lambda c: natural_sort(c.getRef()))   
        
    #update a given field, based on some rules and such
    def updateField(self, field, fieldData):
        
        if field in ColumnList._COLUMNS_PROTECTED: return

        if (field == None or field == ""): return
        elif fieldData == "" or fieldData == None:
            return
        elif (not field in self.fields.keys()) or (self.fields[field] == None) or (self.fields[field] == ""):
            self.fields[field] = fieldData
        elif fieldData.lower() in self.fields[field].lower():
            return
        else:
            print("Conflict:",self.fields[field],",",fieldData)
            self.fields[field] += " " + fieldData
        
    def updateFields(self, fields = ColumnList._COLUMNS_ALL):
    
        for f in fields:
            
            #get info from each field
            for c in self.components:
                
                self.updateField(f, c.getField(f))
                     
        #update 'global' fields
        self.fields[Column.COL_REFERENCE] = self.getRefs()
        self.fields[Column.COL_GRP_QUANTITY] = self.getCount()
        self.fields[Column.COL_VALUE] = self.components[0].getValue()
        self.fields[Column.COL_PART] = self.components[0].getPartName()
        self.fields[Column.COL_DESCRIPTION] = self.components[0].getDescription()
        self.fields[Column.COL_DATASHEET] = self.components[0].getDatasheet()
        self.fields[Column.COL_FP] = self.components[0].getFootprint().split(":")[-1]
        self.fields[Column.COL_FP_LIB] = self.components[0].getFootprint().split(":")[0]

    #return a dict of the CSV data based on the supplied columns
    def getCSVRow(self, columns):
        row = [self.getCSVField(key) for key in columns]
        return row

    #return a dict of the KiCAD data based on the supplied columns
    def getKicadRow(self, columns):
        row = [self.getField(key) for key in columns]
        #print(row)
        return row

    #return a dict of harmonized data based on the supplied columns
    def getHarmonizedRow(self,columns):
        return [self.getHarmonizedField(key) for key in columns]