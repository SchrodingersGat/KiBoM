
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
    SECTION_EXCLUDE_PART = "EXCLUDE_COMPONENT_PART"
    SECTION_EXCLUDE_DESC = "EXCLUDE_COMPONENT_DESC"
    SECTION_ALIASES = "COMPONENT_ALIASES"
    
    OPT_IGNORE_DNF = "ignore_dnf"
    OPT_NUMBER_ROWS = "number_rows"
    OPT_GROUP_CONN = "group_connectors"
    OPT_USE_REGEX = "test_regex"
    OPT_COMP_FP = "compare_footprints"
    OPT_INC_PRICE = "calculate_price"
    OPT_BUILD_NUMBER = 'build_quantity' 
    
    #list of columns which we can use regex on
    COL_REG_EX = [
        ColumnList.COL_REFERENCE,
        ColumnList.COL_DESCRIPTION,
        ColumnList.COL_VALUE,
        ColumnList.COL_FP,
        ColumnList.COL_FP_LIB,
        ColumnList.COL_PART,
        ColumnList.COL_PART_LIB
        ]

    def __init__(self):
        self.ignore = [
            ColumnList.COL_PART_LIB,
            ColumnList.COL_FP_LIB,
            ] #list of headings to ignore in BoM generation
        self.ignoreDNF = False #ignore rows for do-not-fit parts
        self.numberRows = True #add row-numbers to BoM output
        self.groupConnectors = True #group connectors and ignore component value
        self.useRegex = True #Test various columns with regex
        self.compareFootprints = True #test footprints when comparing components
        self.buildNumber = 0
        
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
            'SOLDER_BRIDGE.*',
            'test'
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
            
        #dictionary of possible regex expressions for ignoring component row(s)
        self.regex = dict.fromkeys(self.COL_REG_EX)
        
        #default regex values
        self.regex[ColumnList.COL_REFERENCE] = [
            'TP[0-9]+',
            ]
            
        self.regex[ColumnList.COL_PART] = [
            'mounthole',
            'scopetest',
            'mount_hole',
            'solder_bridge',
            'test_point',
            ]
            
        self.regex[ColumnList.COL_FP] = [
            'mounthole'
            ]
        
    def columnToGroup(self, col):
        return "REGEXCLUDE_" + col.upper().replace(" ","_")
        
    #check an option within the SECTION_GENERAL group
    def checkOption(self, parser, opt, default=False):
        if parser.has_option(self.SECTION_GENERAL, opt):
            return parser.get(self.SECTION_GENERAL, opt).lower() in ["1","true","yes"]
        else:
            return default
            
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
                self.ignoreDNF =  self.checkOption(cf, self.OPT_IGNORE_DNF, default=True)
                self.numberRows = self.checkOption(cf, self.OPT_NUMBER_ROWS, default=True)
                self.groupConnectors = self.checkOption(cf, self.OPT_GROUP_CONN, default=True)
                self.useRegex = self.checkOption(cf, self.OPT_USE_REGEX, default=True)
                self.compareFootprints = self.checkOption(cf, self.OPT_COMP_FP, default=True)
                    
                if cf.has_option(self.SECTION_GENERAL, self.OPT_BUILD_NUMBER):
                    try:
                        self.buildNumber = int(cf.get(self.SECTION_GENERAL, self.OPT_BUILD_NUMBER))
                        if self.buildNumber < 1:
                            self.buildNumber = 0
                    except:
                        pass
                    
            #read out ignored-rows
            if self.SECTION_IGNORE in cf.sections():
                self.ignore = [i for i in cf.options(self.SECTION_IGNORE)]
            
            #read out component aliases
            if self.SECTION_ALIASES in cf.sections():
                self.aliases = [a.split(" ") for a in cf.options(self.SECTION_ALIASES)]
                
            #read out the regex
            for key in self.regex.keys():
                section = self.columnToGroup(key)
                if section in cf.sections():
                    self.regex[key] = [r for r in cf.options(section)]
            
            
    #add an option to the SECTION_GENRAL group
    def addOption(self, parser, opt, value, comment=None):
        if comment:
            if not comment.startswith(";"):
                comment = "; " + comment
            parser.set(self.SECTION_GENERAL, comment)
        parser.set(self.SECTION_GENERAL, opt, "1" if value else "0")
            
    #write KiBOM preferences to file
    def Write(self, file):
        file = os.path.abspath(file)
        
        cf = ConfigParser.RawConfigParser(allow_no_value = True)
        
        cf.add_section(self.SECTION_GENERAL)
        cf.set(self.SECTION_GENERAL, "; General BoM options here")
        self.addOption(cf, self.OPT_IGNORE_DNF, self.ignoreDNF, comment="If '{opt}' option is set to 1, rows that are not to be fitted on the PCB will not be written to the BoM file".format(opt=self.OPT_IGNORE_DNF))
        self.addOption(cf, self.OPT_NUMBER_ROWS, self.numberRows, comment="If '{opt}' option is set to 1, each row in the BoM will be prepended with an incrementing row number".format(opt=self.OPT_NUMBER_ROWS))
        self.addOption(cf, self.OPT_GROUP_CONN, self.groupConnectors, comment="If '{opt}' option is set to 1, connectors with the same footprints will be grouped together, independent of the name of the connector".format(opt=self.OPT_GROUP_CONN))
        self.addOption(cf, self.OPT_USE_REGEX, self.useRegex, comment="If '{opt}' option is set to 1, each component group will be tested against a number of regular-expressions (specified, per column, below). If any matches are found, the row is ignored in the output file".format(opt=self.OPT_USE_REGEX))
        self.addOption(cf, self.OPT_COMP_FP, self.compareFootprints, comment="If '{opt}' option is set to 1, two components must have the same footprint to be grouped together. If '{opt}' is not set, then footprint comparison is ignored.".format(opt=self.OPT_COMP_FP))
        cf.set(self.SECTION_GENERAL, "; '{opt}' is the number of boards to build, which is used to calculate total parts quantity. If this is set to zero (0) then it is ignored".format(opt=self.OPT_BUILD_NUMBER))
        cf.set(self.SECTION_GENERAL, self.OPT_BUILD_NUMBER, str(self.buildNumber))
        
        cf.add_section(self.SECTION_IGNORE)
        cf.set(self.SECTION_IGNORE, "; Any column heading that appears here will be excluded from the Generated BoM")
        cf.set(self.SECTION_IGNORE, "; Titles are case-insensitive")
        
        for i in self.ignore:
            cf.set(self.SECTION_IGNORE, i)
            
        cf.add_section(self.SECTION_ALIASES)
        cf.set(self.SECTION_ALIASES, "; A series of values which are considered to be equivalent for the part name")
        cf.set(self.SECTION_ALIASES, "; Each line represents a space-separated list of equivalent component name values")
        cf.set(self.SECTION_ALIASES, "; e.g. 'c c_small cap' will ensure the equivalent capacitor symbols can be grouped together")
        for a in self.aliases:
            cf.set(self.SECTION_ALIASES, " ".join(a))
            
        for col in self.regex.keys():
            
            reg = self.regex[col]
            
            section = self.columnToGroup(col)
            cf.add_section(section)
            #comments
            cf.set(section, "; A list of regex to compare against the '{col}' column".format(col=col))
            cf.set(section, "; If the value in the '{col}' column matches any of these expressions, the row will be excluded from the BoM".format(col=col))
            
            if type(reg) == str:
                cf.set(section, reg)
                
            elif type(reg) == list:
                for r in reg:
                    cf.set(section, r)
            

            
        with open(file, 'wb') as configfile:
            cf.write(configfile)