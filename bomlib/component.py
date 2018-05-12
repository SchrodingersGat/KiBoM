from bomlib.columns import ColumnList
from bomlib.preferences import BomPref
import bomlib.units as units
from bomlib.sort import natural_sort
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

    def compareField(self, other, field):

        this_field = self.getField(field).lower()
        other_field = other.getField(field).lower()

        #if blank comparisons are allowed
        if this_field == "" or other_field == "":
            if not self.prefs.mergeBlankFields:
                return False

        if this_field == other_field: return True

        return False

    #Equivalency operator is used to determine if two parts are 'equal'
    def __eq__(self, other):
        """Equlivalency operator, remember this can be easily overloaded"""

        #'fitted' value must be the same for both parts
        if self.isFitted() != other.isFitted():
            return False

        if len(self.prefs.groups)==0:
            return False

        for c in self.prefs.groups:
            #perform special matches
            if c.lower() == ColumnList.COL_VALUE.lower():
                if not self.compareValue(other):
                    return False
            #match part name
            elif c.lower() == ColumnList.COL_PART.lower():
                if not self.comparePartName(other):
                    return False

            #generic match
            elif not self.compareField(other, c):
                    return False

        return True

    def setLibPart(self, part):
        self.libpart = part

    def getPrefix(self): #return the reference prefix
        #e.g. if this component has a reference U12, will return "U"
        prefix = ""

        for c in self.getRef():
            if c.isalpha(): prefix += c
            else: break

        return prefix

    def getSufix(self): #return the reference sufix #
        #e.g. if this component has a reference U12, will return "12"
        sufix = ""

        for c in self.getRef():
            if c.isalpha(): sufix = ""
            else: sufix += c

        return int(sufix)

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

    def getField(self, name, ignoreCase=True, libraryToo=True):
        """Return the value of a field named name. The component is first
        checked for the field, and then the components library part is checked
        for the field. If the field doesn't exist in either, an empty string is
        returned

        Keywords:
        name -- The name of the field to return the value for
        libraryToo --   look in the libpart's fields for the same name if not found
                        in component itself
        """


        #special fields
        fp = self.getFootprint().split(":")

        if name.lower() == ColumnList.COL_REFERENCE.lower():
            return self.getRef().strip()

        elif name.lower() == ColumnList.COL_DESCRIPTION.lower():
            return self.getDescription().strip()

        elif name.lower() == ColumnList.COL_DATASHEET.lower():
            return self.getDatasheet().strip()

        # Footprint library is first element
        elif name.lower() == ColumnList.COL_FP_LIB.lower():
            if len(fp) > 1:
                return fp[0].strip()
            else:
                return "" # explicit empty return

        elif name.lower() == ColumnList.COL_FP.lower():
            if len(fp) > 1:
                return fp[1].strip()
            elif len(fp) == 1:
                return fp[0]
            else:
                return ""

        elif name.lower() == ColumnList.COL_VALUE.lower():
            return self.getValue().strip()

        elif name.lower() == ColumnList.COL_PART.lower():
            return self.getPartName().strip()

        elif name.lower() == ColumnList.COL_PART_LIB.lower():
            return self.getLibName().strip()

        #other fields (case insensitive)
        for f in self.getFieldNames():
            if f.lower() == name.lower():
                field = self.element.get("field", "name", f)

                if field == "" and libraryToo:
                    field = self.libpart.getField(f)

                return field.strip()

        #could not find a matching field
        return ""

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

        check = self.getField(self.prefs.configField).lower()

        #check the value field first
        if self.getValue().lower() in DNF or check.lower() in DNF:
            return False

        if check == "":
            return True #empty is fitted

        opts = check.split(",")

        result = True

        for opt in opts:
            #options that start with '-' are explicitly removed from certain configurations
            if opt.startswith('-') and opt[1:].lower() == self.prefs.pcbConfig.lower():
                result = False
                break
            if opt.startswith("+"):
                result = False
                if opt[1:].lower() == self.prefs.pcbConfig.lower():
                    result = True

        #by default, part is fitted
        return result

    #test if this part should be included, based on any regex expressions provided in the preferences
    def testRegExclude(self):

        for reg in self.prefs.regExcludes:

            if type(reg) == list and len(reg) == 2:
                field_name, regex = reg
                field_value = self.getField(field_name)

                # Attempt unicode escaping...
                # Filthy hack
                try:
                    regex = regex.decode("unicode_escape")
                except:
                    pass

                if re.search(regex, field_value, flags=re.IGNORECASE) is not None:
                    if self.prefs.verbose:
                        print("Excluding '{ref}': Field '{field}' ({value}) matched '{reg}'".format(
                            ref = self.getRef(),
                            field = field_name,
                            value = field_value,
                            reg = regex))

                    return True #found a match

        #default, could not find any matches
        return False

    def testRegInclude(self):

        if len(self.prefs.regIncludes) == 0: #nothing to match against
            return True

        for reg in self.prefs.regIncludes:

            if type(reg) == list and len(reg) == 2:
                field_name, regex = reg
                field_value = self.getField(field_name)

                print(field_name,field_value,regex)

                if re.search(regex, field_value, flags=re.IGNORECASE) is not None:
                    if self.prefs.verbose:
                        print("")

                    #found a match
                    return True

        #default, could not find a match
        return False

    def getFootprint(self, libraryToo=True):
        ret = self.element.get("footprint")
        if ret =="" and libraryToo:
            ret = self.libpart.getFootprint()
        return ret

    def getDatasheet(self, libraryToo=True):
        ret = self.element.get("datasheet")
        if ret =="" and libraryToo:
            ret = self.libpart.getDatasheet()
        return ret

    def getTimestamp(self):
        return self.element.get("tstamp")

    def getDescription(self, libraryToo=True):
        ret = self.element.get("field", "name", "Description")
        if ret =="" and libraryToo:
            ret = self.libpart.getDescription()
        return ret

class joiner:
    def __init__(self):
      self.stack = []

    def add(self, P, N):

        if self.stack == []:
            self.stack.append(((P,N),(P,N)))
            return

        S, E = self.stack[-1]

        if N == E[1]+1:
            self.stack[-1] = (S, (P,N))
        else:
            self.stack.append(((P,N),(P,N)))

    def flush(self, sep, N=None, dash='-'):
        refstr = u''
        c = 0
        for Q in self.stack:
            if N!=None and c%N==0 and c!=0:
                refstr+=u'\n'
            elif c!=0:
                refstr+=sep

            S, E = Q
            if S == E:
                refstr+="%s%d"%S
                c+=1
            else:
                #do we have space?
                if (c+1)%N==0: #no
                    refstr+=u'\n'
                    c += 1

                refstr+="%s%d%s%s%d"%(S[0],S[1],dash,E[0],E[1])
                c+=2
        return refstr

class ComponentGroup():

    """
    Initialize the group with no components, and default fields
    """
    def __init__(self, prefs=None):
        self.components = []
        self.fields = dict.fromkeys(ColumnList._COLUMNS_DEFAULT)    #columns loaded from KiCad

        if not prefs:
            prefs = BomPref()

        self.prefs = prefs

    def getField(self, field):

        if not field in self.fields.keys(): return ""
        if not self.fields[field]: return ""
        return u''.join((self.fields[field]))

    def getCount(self):
        return len(self.components)

    #Test if a given component fits in this group
    def matchComponent(self, c):
        if len(self.components) == 0: return True
        if c == self.components[0]: return True

        return False

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

    def getAltRefs(self, wrapN=None):
        S = joiner()

        for n in self.components:
                P, N = (n.getPrefix(), n.getSufix())
                S.add(P,N)

        return S.flush(' ', N=wrapN)

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
            print("Field conflict: ({refs}) [{name}] : '{flds}' <- '{fld}'".format(
                refs = self.getRefs(),
                name = field,
                flds = self.fields[field],
                fld = fieldData))
            self.fields[field] += " " + fieldData

    def updateFields(self, usealt=False, wrapN=None):
        for c in self.components:
            for f in c.getFieldNames():

                #these columns are handled explicitly below
                if f in ColumnList._COLUMNS_PROTECTED:
                    continue

                self.updateField(f, c.getField(f))

        #update 'global' fields
        if usealt:
            self.fields[ColumnList.COL_REFERENCE] = self.getAltRefs(wrapN)
        else:
            self.fields[ColumnList.COL_REFERENCE] = self.getRefs()

        q = self.getCount()
        self.fields[ColumnList.COL_GRP_QUANTITY] = "{n}{dnf}".format(
            n=q,
            dnf = " (DNF)" if not self.isFitted() else "")

        self.fields[ColumnList.COL_GRP_BUILD_QUANTITY] = str(q * self.prefs.boards) if self.isFitted() else "0"
        self.fields[ColumnList.COL_VALUE] = self.components[0].getValue()
        self.fields[ColumnList.COL_PART] = self.components[0].getPartName()
        self.fields[ColumnList.COL_PART_LIB] = self.components[0].getLibName()
        self.fields[ColumnList.COL_DESCRIPTION] = self.components[0].getDescription()
        self.fields[ColumnList.COL_DATASHEET] = self.components[0].getDatasheet()

        # Footprint field requires special attention
        fp = self.components[0].getFootprint().split(":")

        if len(fp) >= 2:
            self.fields[ColumnList.COL_FP_LIB] = fp[0]
            self.fields[ColumnList.COL_FP] = fp[1]
        elif len(fp) == 1:
            self.fields[ColumnList.COL_FP_LIB] = ""
            self.fields[ColumnList.COL_FP] = fp[0]
        else:
            self.fields[ColumnList.COL_FP_LIB] = ""
            self.fields[ColumnList.COL_FP] = ""

    #return a dict of the KiCad data based on the supplied columns
    #NOW WITH UNICODE SUPPORT!
    def getRow(self, columns):
        row = []
        for key in columns:
            val = self.getField(key)

            if val is None:
                val = ""
            else:
                val = u'' + val
                val = val.encode('utf-8')

            row.append(val)

        return row
