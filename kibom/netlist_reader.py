# -*- coding: utf-8 -*-

"""
    @package
    Generate a HTML BOM list.
    Components are sorted and grouped by value
    Any existing fields are read
"""


from __future__ import print_function
import sys
import os.path
import xml.sax as sax

from .component import Component, ComponentGroup
from .preferences import BomPref
from . import debug


class xmlElement():
    """xml element which can represent all nodes of the netlist tree.  It can be
    used to easily generate various output formats by propogating format
    requests to children recursively.
    """
    def __init__(self, name, parent=None):
        self.name = name
        self.attributes = {}
        self.parent = parent
        self.chars = ""
        self.children = []

    def __str__(self):
        """String representation of this netlist element

        """
        return self.name + "[" + self.chars + "]" + " attr_count:" + str(len(self.attributes))

    def addAttribute(self, attr, value):
        """Add an attribute to this element"""
        self.attributes[attr] = value

    def setAttribute(self, attr, value):
        """Set an attributes value - in fact does the same thing as add
        attribute

        """
        self.attributes[attr] = value

    def setChars(self, chars):
        """Set the characters for this element"""
        self.chars = chars

    def addChars(self, chars):
        """Add characters (textual value) to this element"""
        self.chars += chars

    def addChild(self, child):
        """Add a child element to this element"""
        self.children.append(child)
        return self.children[len(self.children) - 1]

    def getParent(self):
        """Get the parent of this element (Could be None)"""
        return self.parent

    def getChild(self, name):
        """Returns the first child element named 'name'

        Keywords:
        name -- The name of the child element to return"""
        for child in self.children:
            if child.name == name:
                return child
        return None

    def getChildren(self, name=None):
        if name:
            # return _all_ children named "name"
            ret = []
            for child in self.children:
                if child.name == name:
                    ret.append(child)
            return ret
        else:
            return self.children

    def get(self, elemName, attribute="", attrmatch=""):
        """Return the text data for either an attribute or an xmlElement
        """
        if (self.name == elemName):
            if attribute != "":
                try:
                    if attrmatch != "":
                        if self.attributes[attribute] == attrmatch:
                            return self.chars
                    else:
                        return self.attributes[attribute]
                except AttributeError:
                    return ""
            else:
                return self.chars

        for child in self.children:
            ret = child.get(elemName, attribute, attrmatch)
            if ret != "":
                return ret

        return ""


class libpart():
    """Class for a library part, aka 'libpart' in the xml netlist file.
    (Components in eeschema are instantiated from library parts.)
    This part class is implemented by wrapping an xmlElement with accessors.
    This xmlElement instance is held in field 'element'.
    """
    def __init__(self, xml_element):
        #
        self.element = xml_element

    def getLibName(self):
        return self.element.get("libpart", "lib")

    def getPartName(self):
        return self.element.get("libpart", "part")

    # For backwards Compatibility with v4.x only
    def getDescription(self):
        return self.element.get("description")

    def getDocs(self):
        return self.element.get("docs")

    def getField(self, name):
        return self.element.get("field", "name", name)

    def getFieldNames(self):
        """Return a list of field names in play for this libpart.
        """
        fieldNames = []
        fields = self.element.getChild('fields')
        if fields:
            for f in fields.getChildren():
                fieldNames.append(f.get('field', 'name'))
        return fieldNames

    def getDatasheet(self):

        datasheet = self.getField("Datasheet")

        if not datasheet or datasheet == "":
            docs = self.getDocs()

            if "http" in docs or ".pdf" in docs:
                datasheet = docs

        return datasheet

    def getFootprint(self):
        return self.getField("Footprint")

    def getAliases(self):
        """Return a list of aliases or None"""
        aliases = self.element.getChild("aliases")
        if aliases:
            ret = []
            children = aliases.getChildren()
            # grab the text out of each child:
            for child in children:
                ret.append(child.get("alias"))
            return ret
        return None


class netlist():
    """ KiCad generic netlist class. Generally loaded from a KiCad generic
    netlist file. Includes several helper functions to ease BOM creating
    scripts

    """
    def __init__(self, fname="", prefs=None):
        """Initialiser for the genericNetlist class

        Keywords:
        fname -- The name of the generic netlist file to open (Optional)

        """
        self.design = None
        self.components = []
        self.libparts = []
        self.libraries = []
        self.nets = []

        # The entire tree is loaded into self.tree
        self.tree = []

        self._curr_element = None

        if not prefs:
            prefs = BomPref()  # Default values

        self.prefs = prefs

        if fname != "":
            self.load(fname)

    def addChars(self, content):
        """Add characters to the current element"""
        self._curr_element.addChars(content)

    def addElement(self, name):
        """Add a new KiCad generic element to the list"""
        if self._curr_element is None:
            self.tree = xmlElement(name)
            self._curr_element = self.tree
        else:
            self._curr_element = self._curr_element.addChild(
                xmlElement(name, self._curr_element))

        # If this element is a component, add it to the components list
        if self._curr_element.name == "comp":
            self.components.append(Component(self._curr_element, prefs=self.prefs))

        # Assign the design element
        if self._curr_element.name == "design":
            self.design = self._curr_element

        # If this element is a library part, add it to the parts list
        if self._curr_element.name == "libpart":
            self.libparts.append(libpart(self._curr_element))

        # If this element is a net, add it to the nets list
        if self._curr_element.name == "net":
            self.nets.append(self._curr_element)

        # If this element is a library, add it to the libraries list
        if self._curr_element.name == "library":
            self.libraries.append(self._curr_element)

        return self._curr_element

    def endDocument(self):
        """Called when the netlist document has been fully parsed"""
        # When the document is complete, the library parts must be linked to
        # the components as they are seperate in the tree so as not to
        # duplicate library part information for every component
        for c in self.components:
            for p in self.libparts:
                if p.getLibName() == c.getLibName():
                    if p.getPartName() == c.getPartName():
                        c.setLibPart(p)
                        break
                    else:
                        aliases = p.getAliases()
                        if aliases and self.aliasMatch(c.getPartName(), aliases):
                            c.setLibPart(p)
                            break

            if not c.getLibPart():
                debug.warning('missing libpart for ref:', c.getRef(), c.getPartName(), c.getLibName())

    def aliasMatch(self, partName, aliasList):
        for alias in aliasList:
            if partName == alias:
                return True
        return False

    def endElement(self):
        """End the current element and switch to its parent"""
        self._curr_element = self._curr_element.getParent()

    def getDate(self):
        """Return the date + time string generated by the tree creation tool"""
        if (sys.version_info[0] >= 3):
            return self.design.get("date")
        else:
            return self.design.get("date").encode('ascii', 'ignore')

    def getSource(self):

        path = self.design.get("source").replace("\\", "/")
        path = os.path.basename(path)

        """Return the source string for the design"""
        if (sys.version_info[0] >= 3):
            return path
        else:
            return path.encode('ascii', 'ignore')

    def getTool(self):
        """Return the tool string which was used to create the netlist tree"""
        if (sys.version_info[0] >= 3):
            return self.design.get("tool")
        else:
            return self.design.get("tool").encode('ascii', 'ignore')

    def getSheet(self):
        return self.design.getChild("sheet")

    def getSheetDate(self):
        sheet = self.getSheet()
        if sheet is None:
            return ""
        return sheet.get("date")

    def getVersion(self):
        """Return the verison of the sheet info"""

        sheet = self.getSheet()
        
        if sheet is None:
            return ""
        
        return sheet.get("rev")

    def getInterestingComponents(self):

        # Copy out the components
        ret = [c for c in self.components]

        # Sort first by ref as this makes for easier to read BOM's
        ret.sort(key=lambda g: g.getRef())

        return ret

    def groupComponents(self, components):

        groups = []

        # Iterate through each component, and test whether a group for these already exists
        for c in components:

            if self.prefs.useRegex:
                # Skip components if they do not meet regex requirements
                if not c.testRegInclude():
                    continue
                if c.testRegExclude():
                    continue

            found = False

            for g in groups:
                if g.matchComponent(c):
                    g.addComponent(c)
                    found = True
                    break

            if not found:
                g = ComponentGroup(prefs=self.prefs)  # Pass down the preferences
                g.addComponent(c)
                groups.append(g)

        # Sort the references within each group
        for g in groups:
            g.sortComponents()
            g.updateFields(self.prefs.useAlt)

        # Sort the groups
        # First priority is the Type of component (e.g. R?, U?, L?)
        groups = sorted(groups, key=lambda g: [g.components[0].getPrefix(), g.components[0].getValueSort()])

        return groups

    def load(self, fname):
        """Load a KiCad generic netlist

        Keywords:
        fname -- The name of the generic netlist file to open

        """
        try:
            self._reader = sax.make_parser()
            self._reader.setContentHandler(_gNetReader(self))
            self._reader.parse(fname)
        except IOError as e:
            debug.error(__file__, ":", e)
            sys.exit(-1)


class _gNetReader(sax.handler.ContentHandler):
    """SAX KiCad generic netlist content handler - passes most of the work back
    to the 'netlist' class which builds a complete tree in RAM for the design

    """
    def __init__(self, aParent):
        self.parent = aParent

    def startElement(self, name, attrs):
        """Start of a new XML element event"""
        element = self.parent.addElement(name)

        for name in attrs.getNames():
            element.addAttribute(name, attrs.getValue(name))

    def endElement(self, name):
        self.parent.endElement()

    def characters(self, content):
        # Ignore erroneous white space - ignoreableWhitespace does not get rid
        # of the need for this!
        if not content.isspace():
            self.parent.addChars(content)

    def endDocument(self):
        """End of the XML document event"""
        self.parent.endDocument()
