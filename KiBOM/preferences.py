
import sys

if sys.version_info.major >= 3:
    import configparser as ConfigParser
else:
    import ConfigParser
import os
from columns import ColumnList

class BomPref:
    
    SECTION_IGNORE = "IGNORE_COLUMNS"
    SECTION_GENERAL = "BOM_OPTIONS"
    SECTION_EXCLUDE_VALUES = "EXCLUDE_COMPONENT_VALUES"
    SECTION_EXCLUDE_REFS = "EXCLUDE_COMPONENT_REFS"
    SECTION_EXCLUDE_FP = "EXCLUDE_COMPONENT_FP"
    SECTION_ALIASES = "COMPONENT_ALIASES"
    
    OPT_IGNORE_DNF = "ignore_dnf"
    OPT_NUMBER_ROWS = "number_rows"
    OPT_GROUP_CONN = "group_connectors"

    def __init__(self):
        self.ignore = [
            ColumnList.COL_PART_LIB,
            ColumnList.COL_FP_LIB,
            ] #list of headings to ignore in BoM generation
        self.ignoreDNF = False #ignore rows for do-not-fit parts
        self.numberRows = True #add row-numbers to BoM output
        self.groupConnectors = True #group connectors and ignore component value
        
        #default reference exclusions
        self.excluded_references = [
            "TP[0-9]+"
            ]
            
        #default value exclusions
        self.excluded_values = [
            'MOUNTHOLE',
            'SCOPETEST',
            'MOUNT_HOLE',
            'MOUNTING_HOLE',
            'SOLDER_BRIDGE.*'
            ]
            
        #default footprint exclusions
        self.excluded_footprints = [
            ]
            
        #default component groupings
        self.aliases = [
            ["c", "c_small", "cap", "capacitor"],
            ["r", "r_small", "res", "resistor"],
            ["sw", "switch"],
            ["l", "l_small", "inductor"]
            ]
        
    #read KiBOM preferences from file
    def Read(self, file, verbose=False):
        file = os.path.abspath(file)
        if not os.path.exists(file) or not os.path.isfile(file):
            print("{f} is not a valid file!".format(f=file))
            return
            
        with open(file, 'rb') as configfile:
            cf = ConfigParser.RawConfigParser(allow_no_value = True)
            
            cf.read(file)
            
            #read general options
            if self.SECTION_GENERAL in cf.sections():
                if cf.has_option(self.SECTION_GENERAL, self.OPT_IGNORE_DNF):
                    self.ignoreDNF = cf.get(self.SECTION_GENERAL, self.OPT_IGNORE_DNF) == "1"
                if cf.has_option(self.SECTION_GENERAL, self.OPT_NUMBER_ROWS):
                    self.numberRows = cf.get(self.SECTION_GENERAL, self.OPT_NUMBER_ROWS) == "1"
                if cf.has_option(self.SECTION_GENERAL, self.OPT_GROUP_CONN):
                    self.groupConnectors = cf.get(self.SECTION_GENERAL, self.OPT_GROUP_CONN) == "1"
                    
            #read out ignored-rows
            if self.SECTION_IGNORE in cf.sections():
                self.ignore = [i for i in cf.options(self.SECTION_IGNORE)]
                
            #read out excluded values
            if self.SECTION_EXCLUDE_VALUES in cf.sections():
                self.excludedValues = [e for e in cf.options(self.SECTION_EXCLUDE_VALUES)]
                
            #read out excluded values
            if self.SECTION_EXCLUDE_REFS in cf.sections():
                self.excludedValues = [e for e in cf.options(self.SECTION_EXCLUDE_REFS)]
                
            #read out excluded values
            if self.SECTION_EXCLUDE_FP in cf.sections():
                self.excludedValues = [e for e in cf.options(self.SECTION_EXCLUDE_FP)]
                
            #read out component aliases
            if self.SECTION_ALIASES in cf.sections():
                self.aliases = [a.split(" ") for a in cf.options(self.SECTION_ALIASES)]
                
            
    #write KiBOM preferences to file
    def Write(self, file):
        file = os.path.abspath(file)
        
        cf = ConfigParser.RawConfigParser(allow_no_value = True)
        
        cf.add_section(self.SECTION_GENERAL)
        cf.set(self.SECTION_GENERAL, "; General BoM options here")
        cf.set(self.SECTION_GENERAL, "; If {opt} option is set to 1, rows that are not to be fitted on the PCB will not be written to the BoM file".format(opt=self.OPT_IGNORE_DNF))
        cf.set(self.SECTION_GENERAL, self.OPT_IGNORE_DNF, 1 if self.ignoreDNF else 0)
        cf.set(self.SECTION_GENERAL, "; If {opt} option is set to 1, each row in the BoM will be prepended with an incrementing row number".format(opt=self.OPT_NUMBER_ROWS))
        cf.set(self.SECTION_GENERAL, self.OPT_NUMBER_ROWS, 1 if self.numberRows else 0)
        cf.set(self.SECTION_GENERAL, "; If {opt} option is set to 1, connectors with the same footprints will be grouped together, independent of the name of the connector".format(opt=self.OPT_GROUP_CONN))
        cf.set(self.SECTION_GENERAL, self.OPT_GROUP_CONN, 1 if self.groupConnectors else 0)
        
        cf.add_section(self.SECTION_IGNORE)
        cf.set(self.SECTION_IGNORE, "; Any column heading that appears here will be excluded from the Generated BoM")
        cf.set(self.SECTION_IGNORE, "; Titles are case-insensitive")
        
        for i in self.ignore:
            cf.set(self.SECTION_IGNORE, i)
            
        cf.add_section(self.SECTION_EXCLUDE_VALUES)
        cf.set(self.SECTION_EXCLUDE_VALUES, "; A series of reg-ex strings for ignoring component values")
        cf.set(self.SECTION_EXCLUDE_VALUES, "; Any components with values that match any of these reg-ex strings will be ignored")
        for e in self.excluded_values:
            cf.set(self.SECTION_EXCLUDE_VALUES, e)
            
        cf.add_section(self.SECTION_EXCLUDE_REFS)
        cf.set(self.SECTION_EXCLUDE_REFS, "; A series of reg-ex strings for ignoring component references")
        cf.set(self.SECTION_EXCLUDE_REFS, "; Any components with references that match any of these reg-ex strings will be ignored")
        for e in self.excluded_references:
            cf.set(self.SECTION_EXCLUDE_REFS, e)
            
        cf.add_section(self.SECTION_EXCLUDE_FP)
        cf.set(self.SECTION_EXCLUDE_FP, "; A series of reg-ex strings for ignoring component footprints")
        cf.set(self.SECTION_EXCLUDE_FP, "; Any components with footprints that match any of these reg-ex strings will be ignored")
        for e in self.excluded_footprints:
            cf.set(self.SECTION_EXCLUDE_FP, e)
            
        cf.add_section(self.SECTION_ALIASES)
        cf.set(self.SECTION_ALIASES, "; A series of values which are considered to be equivalent for the part name")
        cf.set(self.SECTION_ALIASES, "; Each line represents a space-separated list of equivalent component name values")
        cf.set(self.SECTION_ALIASES, "; e.g. 'c c_small cap' will ensure the equivalent capacitor symbols can be grouped together")
        for a in self.aliases:
            cf.set(self.SECTION_ALIASES, " ".join(a))
            
        with open(file, 'wb') as configfile:
            cf.write(configfile)