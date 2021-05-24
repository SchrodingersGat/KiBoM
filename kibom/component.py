# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import sys

from .columns import ColumnList
from .preferences import BomPref
from . import units
from . import debug
from .sort import natural_sort

# String matches for marking a component as "do not fit"
DNF = [
    "dnf",
    "dnl",
    "dnp",
    "do not fit",
    "do not place",
    "do not load",
    "nofit",
    "nostuff",
    "noplace",
    "noload",
    "not fitted",
    "not loaded",
    "not placed",
    "no stuff",
]

# String matches for marking a component as "do not change" or "fixed"
DNC = [
    "dnc",
    "do not change",
    "no change",
    "fixed"
]


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

    # Compare the value of this part, to the value of another part (see if they match)
    def compareValue(self, other):
        # Simple string comparison
        if self.getValue().lower() == other.getValue().lower():
            return True

        # Otherwise, perform a more complicated value comparison
        if units.compareValues(self.getValue(), other.getValue()):
            return True

        # Ignore value if both components are connectors
        if self.prefs.groupConnectors:
            if 'connector' in self.getLibName().lower() and 'connector' in other.getLibName().lower():
                return True

        # No match, return False
        return False

    # Determine if two parts have the same name
    def comparePartName(self, other):
        pn1 = self.getPartName().lower()
        pn2 = other.getPartName().lower()

        # Simple direct match
        if pn1 == pn2:
            return True

        # Compare part aliases e.g. "c" to "c_small"
        for alias in self.prefs.aliases:
            if pn1 in alias and pn2 in alias:
                return True

        return False

    def compareField(self, other, field):

        this_field = self.getField(field).lower()
        other_field = other.getField(field).lower()

        # If blank comparisons are allowed
        if this_field == "" or other_field == "":
            if not self.prefs.mergeBlankFields:
                return False

        if this_field == other_field:
            return True

        return False

    def __eq__(self, other):
        """
        Equivalency operator is used to determine if two parts are 'equal'
        """
        
        # 'fitted' value must be the same for both parts
        if self.isFitted() != other.isFitted():
            return False

        # 'fixed' value must be the same for both parts
        if self.isFixed() != other.isFixed():
            return False

        if len(self.prefs.groups) == 0:
            return False

        for c in self.prefs.groups:
            # Perform special matches
            if c.lower() == ColumnList.COL_VALUE.lower():
                if not self.compareValue(other):
                    return False
            # Match part name
            elif c.lower() == ColumnList.COL_PART.lower():
                if not self.comparePartName(other):
                    return False

            # Generic match
            elif not self.compareField(other, c):
                return False

        return True

    def setLibPart(self, part):
        self.libpart = part

    def getPrefix(self):
        """
        Get the reference prefix
        e.g. if this component has a reference U12, will return "U"
        """
        
        prefix = ""

        for c in self.getRef():
            if c.isalpha():
                prefix += c
            else:
                break

        return prefix

    def getSuffix(self):
        """
        Return the reference suffix #
        e.g. if this component has a reference U12, will return "12"
        """
        
        suffix = ""

        for c in self.getRef():
            if c.isalpha():
                suffix = ""
            else:
                suffix += c

        return int(suffix)

    def getLibPart(self):
        return self.libpart

    def getPartName(self):
        return self.element.get("libsource", "part")

    def getLibName(self):
        return self.element.get("libsource", "lib")

    def getSheetpathNames(self):
        return self.element.get("sheetpath", "names")

    def getDescription(self):
        try:
            ret = self.element.get("libsource", "description")
        except:
            # Compatibility with old KiCad versions (4.x)
            ret = self.element.get("field", "name", "description")

        if ret == "":
            try:
                ret = self.libpart.getDescription()
            except AttributeError:
                # Raise a good error description here, so the user knows what the culprit component is.
                # (sometimes libpart is None)
                raise AttributeError('Could not get description for part {}{}.'.format(self.getPrefix(),
                                     self.getSuffix()))

        return ret

    def setValue(self, value):
        """Set the value of this component"""
        v = self.element.getChild("value")
        if v:
            v.setChars(value)

    def getValue(self):
        return self.element.get("value")

    # Try to better sort R, L and C components
    def getValueSort(self):
        pref = self.getPrefix()
        if pref in 'RLC' or pref == 'RV':
            res = units.compMatch(self.getValue())
            if res:
                value, mult, unit = res
                if pref in "CL":
                    # fempto Farads
                    value = "{0:15d}".format(int(value * 1e15 * mult + 0.1))
                else:
                    # milli Ohms
                    value = "{0:15d}".format(int(value * 1000 * mult + 0.1))
                return value
        return self.element.get("value")

    def setField(self, name, value):
        """ Set the value of the specified field """

        # Description field
        doc = self.element.getChild('libsource')
        if doc:
            for att_name, att_value in doc.attributes.items():
                if att_name.lower() == name.lower():
                    doc.attributes[att_name] = value
                    return value

        # Common fields
        field = self.element.getChild(name.lower())
        if field:
            field.setChars(value)
            return value

        # Other fields
        fields = self.element.getChild('fields')
        if fields:
            for field in fields.getChildren():
                if field.get('field', 'name') == name:
                    field.setChars(value)
                    return value

        return None

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
                # Explicit empty return
                return ""

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

        elif name.lower() == ColumnList.COL_SHEETPATH.lower():
            return self.getSheetpathNames().strip()

        # Other fields (case insensitive)
        for f in self.getFieldNames():
            if f.lower() == name.lower():
                field = self.element.get("field", "name", f)

                if field == "" and libraryToo:
                    field = self.libpart.getField(f)

                return field.strip()

        # Could not find a matching field
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
                fieldNames.append(f.get('field', 'name'))
        
        return fieldNames

    def getRef(self):
        return self.element.get("comp", "ref")

    def isFitted(self):
        """ Determine if a component is FITTED or not """

        # Check the value field first
        if self.getValue().lower() in DNF:
            return False

        check = self.getField(self.prefs.configField).lower()
        # Empty value means part is fitted
        if check == "":
            return True

        # Also support space separated list (simple cases)
        opts = check.split(" ")
        for opt in opts:
            if opt.lower() in DNF:
                return False

        # Variants logic
        opts = check.split(",")
        # Exclude components that match a -VARIANT
        for opt in opts:
            opt = opt.strip()
            # Any option containing a DNF is not fitted
            if opt in DNF:
                return False
            # Options that start with '-' are explicitly removed from certain configurations
            if opt.startswith("-") and opt[1:] in self.prefs.pcbConfig:
                return False
        # Include components that match +VARIANT
        exclusive = False
        for opt in opts:
            # Options that start with '+' are fitted only for certain configurations
            if opt.startswith("+"):
                exclusive = True
                if opt[1:] in self.prefs.pcbConfig:
                    return True
        # No match
        return not exclusive

    def isFixed(self):
        """ Determine if a component is FIXED or not.
            Fixed components shouldn't be replaced without express authorization """

        # Check the value field first
        if self.getValue().lower() in DNC:
            return True

        check = self.getField(self.prefs.configField).lower()
        # Empty is not fixed
        if check == "":
            return False

        opts = check.split(" ")
        for opt in opts:
            if opt.lower() in DNC:
                return True

        opts = check.split(",")
        for opt in opts:
            if opt.lower() in DNC:
                return True

        return False

    # Test if this part should be included, based on any regex expressions provided in the preferences
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
                    debug.info("Excluding '{ref}': Field '{field}' ({value}) matched '{reg}'".format(
                        ref=self.getRef(),
                        field=field_name,
                        value=field_value,
                        reg=regex).encode('utf-8')
                    )

                    # Found a match
                    return True

        # Default, could not find any matches
        return False

    def testRegInclude(self):

        if len(self.prefs.regIncludes) == 0:  # Nothing to match against
            return True

        for reg in self.prefs.regIncludes:

            if type(reg) == list and len(reg) == 2:
                field_name, regex = reg
                field_value = self.getField(field_name)

                debug.info(field_name, field_value, regex)

                if re.search(regex, field_value, flags=re.IGNORECASE) is not None:

                    # Found a match
                    return True

        # Default, could not find a match
        return False

    def getFootprint(self, libraryToo=True):
        ret = self.element.get("footprint")
        if ret == "" and libraryToo:
            if self.libpart:
                ret = self.libpart.getFootprint()
        return ret

    def getDatasheet(self, libraryToo=True):
        ret = self.element.get("datasheet")
        if ret == "" and libraryToo:
            ret = self.libpart.getDatasheet()
        return ret

    def getTimestamp(self):
        return self.element.get("tstamp")


class joiner:
    def __init__(self):
        self.stack = []

    def add(self, P, N):
        
        if self.stack == []:
            self.stack.append(((P, N), (P, N)))
            return

        S, E = self.stack[-1]

        if N == E[1] + 1:
            self.stack[-1] = (S, (P, N))
        else:
            self.stack.append(((P, N), (P, N)))

    def flush(self, sep, N=None, dash='-'):

        refstr = u''
        c = 0

        for Q in self.stack:
            if bool(N) and c != 0 and c % N == 0:
                refstr += u'\n'
            elif c != 0:
                refstr += sep + " "

            S, E = Q

            if S == E:
                refstr += "%s%d" % S
                c += 1
            else:
                # Do we have space?
                if bool(N) and (c + 1) % N == 0:
                    refstr += u'\n'
                    c += 1

                refstr += "%s%d%s%s%d" % (S[0], S[1], dash, E[0], E[1])
                c += 2
        return refstr


class ComponentGroup():

    """
    Initialize the group with no components, and default fields
    """
    def __init__(self, prefs=None):
        self.components = []
        self.fields = dict.fromkeys(ColumnList._COLUMNS_DEFAULT)  # Columns loaded from KiCad

        if not prefs:
            prefs = BomPref()

        self.prefs = prefs

    def getField(self, field):

        if field not in self.fields.keys():
            return ""
        
        if not self.fields[field]:
            return ""
        
        return u''.join((self.fields[field]))

    def getCount(self):
        return len(self.components)

    # Test if a given component fits in this group
    def matchComponent(self, c):
        if len(self.components) == 0:
            return True
        if c == self.components[0]:
            return True

        return False

    def containsComponent(self, c):
        # Test if a given component is already contained in this grop
        if not self.matchComponent(c):
            return False

        for comp in self.components:
            if comp.getRef() == c.getRef():
                return True

        return False

    def addComponent(self, c):
        # Add a component to the group

        if len(self.components) == 0:
            self.components.append(c)
        elif self.containsComponent(c):
            return
        elif self.matchComponent(c):
            self.components.append(c)

    def isFitted(self):
        return any([c.isFitted() for c in self.components])

    def isFixed(self):
        return any([c.isFixed() for c in self.components])

    def getRefs(self):
        # Return a list of the components
        separator = self.prefs.refSeparator
        return separator.join([c.getRef() for c in self.components])

    def getAltRefs(self):
        S = joiner()

        for n in self.components:
            P, N = (n.getPrefix(), n.getSuffix())
            S.add(P, N)

        return S.flush(self.prefs.refSeparator)

    # Sort the components in correct order
    def sortComponents(self):
        self.components = sorted(self.components, key=lambda c: natural_sort(c.getRef()))

    # Update a given field, based on some rules and such
    def updateField(self, field, fieldData):

        # Protected fields cannot be overwritten
        if field in ColumnList._COLUMNS_PROTECTED:
            return

        if field is None or field == "":
            return
        elif fieldData == "" or fieldData is None:
            return

        if (field not in self.fields.keys()) or (self.fields[field] is None) or (self.fields[field] == ""):
            self.fields[field] = fieldData
        elif fieldData.lower() in self.fields[field].lower():
            return
        else:
            debug.warning("Field conflict: ({refs}) [{name}] : '{flds}' <- '{fld}'".format(
                refs=self.getRefs(),
                name=field,
                flds=self.fields[field],
                fld=fieldData).encode('utf-8'))
            self.fields[field] += " " + fieldData

    def updateFields(self, usealt=False, wrapN=None):
        for c in self.components:
            for f in c.getFieldNames():

                # These columns are handled explicitly below
                if f in ColumnList._COLUMNS_PROTECTED:
                    continue

                self.updateField(f, c.getField(f))

        # Update 'global' fields
        if usealt:
            self.fields[ColumnList.COL_REFERENCE] = self.getAltRefs()
        else:
            self.fields[ColumnList.COL_REFERENCE] = self.getRefs()

        q = self.getCount()
        self.fields[ColumnList.COL_GRP_QUANTITY] = "{n}{dnf}{dnc}".format(
            n=q,
            dnf=" (DNF)" if not self.isFitted() else "",
            dnc=" (DNC)" if self.isFixed() else "")

        self.fields[ColumnList.COL_GRP_BUILD_QUANTITY] = str(q * self.prefs.boards) if self.isFitted() else "0"
        self.fields[ColumnList.COL_VALUE] = self.components[0].getValue()
        self.fields[ColumnList.COL_PART] = self.components[0].getPartName()
        self.fields[ColumnList.COL_PART_LIB] = self.components[0].getLibName()
        self.fields[ColumnList.COL_DESCRIPTION] = self.components[0].getDescription()
        self.fields[ColumnList.COL_DATASHEET] = self.components[0].getDatasheet()
        self.fields[ColumnList.COL_SHEETPATH] = self.components[0].getSheetpathNames()

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

    # Return a dict of the KiCad data based on the supplied columns
    # NOW WITH UNICODE SUPPORT!
    def getRow(self, columns):
        row = []
        for key in columns:
            val = self.getField(key)

            # Join fields (appending to current value) (#81)
            for join_l in self.prefs.join:
                # Each list is "target, source..." so we need at least 2 elements
                elements = len(join_l)
                target = join_l[0]
                if elements > 1 and target == key:
                    # Append data from the other fields
                    for source in join_l[1:]:
                        v = self.getField(source)
                        if v:
                            val = val + ' ' + v

            if val is None:
                val = ""
            else:
                val = u'' + val
                if sys.version_info[0] < 3:
                    val = val.encode('utf-8')

            row.append(val)

        return row
