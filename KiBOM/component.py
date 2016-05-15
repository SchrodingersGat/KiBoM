from columns import ColumnList
from preferences import BomPref
import units
from sort import natural_sort
import re

DNF = ["dnf", "do not fit", "nofit", "no stuff", "nostuff", "noload", "do not load"]

class Component():
    """Class for a component, aka 'comp' in the xml netlist file.
    This component class is implemented by wrapping an xmlElement instance
    with accessors.  The xmlElement is held in field 'element'.
    """

    def __init__(self, xml_element, prefs=None):
        self.element = xml_element
        self.libpart = None
        
        if not prefs:
            prefs = BomPref()
            
        self.prefs = prefs

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
        for alias in self.prefs.aliases:
            if pn1 in alias and pn2 in alias:
                return True

        return False

    #Equivalency operator is used to determine if two parts are 'equal'
    def __eq__(self, other):
        """Equlivalency operator, remember this can be easily overloaded"""

        valueResult = self.compareValue(other)

        #if connector comparison is overridden, set valueResult to True
        if self.prefs.groupConnectors:
            if "conn" in self.getDescription().lower():
                valueResult = True

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
    def __init__(self, prefs=None):
        self.components = []
        self.fields = dict.fromkeys(ColumnList._COLUMNS_PROTECTED)    #columns loaded from KiCAD
        self.csvFields = dict.fromkeys(ColumnList._COLUMNS_DEFAULT) #columns loaded from .csv file
        
        if not prefs:
            prefs = BomPref()
            
        self.prefs = prefs
        
    def getField(self, field):
        if not field in self.fields.keys(): return ""
        if not self.fields[field]: return ""
        return str(self.fields[field])
        
    def getCount(self):
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
        
        #protected fields cannot be overwritten
        if field in ColumnList._COLUMNS_PROTECTED: return

        if (field == None or field == ""): return
        elif fieldData == "" or fieldData == None:
            return
        
        if (not field in self.fields.keys()) or (self.fields[field] == None) or (self.fields[field] == ""):
            self.fields[field] = fieldData
        elif fieldData.lower() in self.fields[field].lower():
            return
        else:
            print("Conflict:",self.fields[field],",",fieldData)
            self.fields[field] += " " + fieldData
        
    def updateFields(self):
    
        for c in self.components:
            for f in c.getFieldNames():
            
                #these columns are handled explicitly below
                if f in ColumnList._COLUMNS_PROTECTED:
                    continue
                    
                self.updateField(f, c.getField(f))
                     
        #update 'global' fields
        self.fields[ColumnList.COL_REFERENCE] = self.getRefs()
        self.fields[ColumnList.COL_GRP_QUANTITY] = "{n}{dnf}".format(
            n = self.getCount(),
            dnf = " (DNF)" if not self.isFitted() else "")
        self.fields[ColumnList.COL_VALUE] = self.components[0].getValue()
        self.fields[ColumnList.COL_PART] = self.components[0].getPartName()
        self.fields[ColumnList.COL_PART_LIB] = self.components[0].getLibName()
        self.fields[ColumnList.COL_DESCRIPTION] = self.components[0].getDescription()
        self.fields[ColumnList.COL_DATASHEET] = self.components[0].getDatasheet()
        
        if len(self.components[0].getFootprint().split(":")) >= 2:
            self.fields[ColumnList.COL_FP] = self.components[0].getFootprint().split(":")[-1]
            self.fields[ColumnList.COL_FP_LIB] = self.components[0].getFootprint().split(":")[0]
        else:
            self.fields[ColumnList.COL_FP] = ""
            self.fields[ColumnList.COL_FP_LIB] = ""
            
    #run test against all available regex exclusions in the preference file
    #return True if none match (i.e. this group is OK)
    #retunr False if any match
    def testRegex(self):
        
        for key in self.prefs.regex.keys():
            reg = self.prefs.regex[key]
            if not type(reg) in [str, list]: continue #regex must be a string, or a list of strings
            #does this group have a column that matches this regex?
            if not self.getField(key): continue
            
            #list of regex to compare against
            if type(reg) is str:
                regex = [reg]
            else:
                regex = reg
                
            #test each regex
            for r in regex:
                field = self.getField(key)
                if re.search(r, field, flags=re.IGNORECASE) is not None:
                    print("'{col}' value '{val}' matched regex '{reg}'".format(
                        col = key,
                        val = self.getField(key),
                        reg = r
                        ))
                    return False
                    
        return True
                

    #return a dict of the KiCAD data based on the supplied columns
    def getRow(self, columns):
        row = [self.getField(key) for key in columns]
        #print(row)
        return row