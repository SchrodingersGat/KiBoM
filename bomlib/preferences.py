
import sys

if sys.version_info.major >= 3:
    import configparser as ConfigParser
else:
    import ConfigParser
import os
from bomlib.columns import ColumnList

class BomPref:

    SECTION_IGNORE = "IGNORE_COLUMNS"
    SECTION_COLUMN_ORDER = "COLUMN_ORDER"
    SECTION_GENERAL = "BOM_OPTIONS"
    SECTION_ALIASES = "COMPONENT_ALIASES"
    SECTION_GROUPING_FIELDS = "GROUP_FIELDS"
    SECTION_REGEXCLUDES = "REGEX_EXCLUDE"
    SECTION_REGINCLUDES = "REGEX_INCLUDE"

    OPT_PCB_CONFIG = "pcb_configuration"
    OPT_NUMBER_ROWS = "number_rows"
    OPT_GROUP_CONN = "group_connectors"
    OPT_USE_REGEX = "test_regex"
    OPT_USE_ALT = "use_alt"
    OPT_ALT_WRAP = "alt_wrap"
    OPT_MERGE_BLANK = "merge_blank_fields"
    OPT_IGNORE_DNF = "ignore_dnf"
    OPT_BACKUP = "make_backup"
    OPT_INCLUDE_VERSION = "include_version_number"

    OPT_CONFIG_FIELD = "fit_field"

    def __init__(self):
        # List of headings to ignore in BoM generation
        self.ignore = [
            ColumnList.COL_PART_LIB,
            ColumnList.COL_FP_LIB,
            ] #list of headings to ignore in BoM generation
        self.corder = ColumnList._COLUMNS_DEFAULT
        self.useAlt = False #use alternate reference representation
        self.altWrap = None #wrap to n items when using alt representation
        self.ignoreDNF = True  # Ignore rows for do-not-fit parts
        self.numberRows = True  # Add row-numbers to BoM output
        self.groupConnectors = True  # Group connectors and ignore component value
        self.useRegex = True  # Test various columns with regex

        self.boards = 1
        self.mergeBlankFields = True  # Blanks fields will be merged when possible
        self.hideHeaders = False
        self.verbose = False  # By default, is not verbose
        self.configField = "Config"  # Default field used for part fitting config
        self.pcbConfig = "default"

        self.backup = "%O.tmp"

        self.separatorCSV = None
        self.includeVersionNumber = True

        # Default fields used to group components
        self.groups = [
            ColumnList.COL_PART,
            ColumnList.COL_PART_LIB,
            ColumnList.COL_VALUE,
            ColumnList.COL_FP,
            ColumnList.COL_FP_LIB,
            # User can add custom grouping columns in bom.ini
            ]

        self.regIncludes = []  # None by default

        self.regExcludes = [
            [ColumnList.COL_REFERENCE,'^TP[0-9]*'],
            [ColumnList.COL_REFERENCE,'^FID'],
            [ColumnList.COL_PART,'mount.*hole'],
            [ColumnList.COL_PART,'solder.*bridge'],
            [ColumnList.COL_PART,'test.*point'],
            [ColumnList.COL_FP,'test.*point'],
            [ColumnList.COL_FP,'mount.*hole'],
            [ColumnList.COL_FP,'fiducial'],
        ]

        # Default component groupings
        self.aliases = [
            ["c", "c_small", "cap", "capacitor"],
            ["r", "r_small", "res", "resistor"],
            ["sw", "switch"],
            ["l", "l_small", "inductor"],
            ["zener","zenersmall"],
            ["d","diode","d_small"]
            ]

    # Check an option within the SECTION_GENERAL group
    def checkOption(self, parser, opt, default=False):
        if parser.has_option(self.SECTION_GENERAL, opt):
            return parser.get(self.SECTION_GENERAL, opt).lower() in ["1","true","yes"]
        else:
            return default

    def checkInt(self, parser, opt, default=False):
        if parser.has_option(self.SECTION_GENERAL, opt):
            return int(parser.get(self.SECTION_GENERAL, opt).lower())
        else:
            return default

    # Read KiBOM preferences from file
    def Read(self, file, verbose=False):
        file = os.path.abspath(file)
        if not os.path.exists(file) or not os.path.isfile(file):
            print("{f} is not a valid file!".format(f=file))
            return

        with open(file, 'rb') as configfile:
            cf = ConfigParser.RawConfigParser(allow_no_value = True)
            cf.optionxform=str

            cf.read(file)

            # Read general options
            if self.SECTION_GENERAL in cf.sections():
                self.ignoreDNF =  self.checkOption(cf, self.OPT_IGNORE_DNF, default=True)
                self.useAlt =  self.checkOption(cf, self.OPT_USE_ALT, default=False)
                self.altWrap =  self.checkInt(cf, self.OPT_ALT_WRAP, default=None)
                self.numberRows = self.checkOption(cf, self.OPT_NUMBER_ROWS, default=True)
                self.groupConnectors = self.checkOption(cf, self.OPT_GROUP_CONN, default=True)
                self.useRegex = self.checkOption(cf, self.OPT_USE_REGEX, default=True)
                self.mergeBlankFields = self.checkOption(cf, self.OPT_MERGE_BLANK, default=True)
                self.includeVersionNumber = self.checkOption(cf, self.OPT_INCLUDE_VERSION, default=True)

            if cf.has_option(self.SECTION_GENERAL, self.OPT_CONFIG_FIELD):
                self.configField = cf.get(self.SECTION_GENERAL, self.OPT_CONFIG_FIELD)

            if cf.has_option(self.SECTION_GENERAL, self.OPT_BACKUP):
                self.backup = cf.get(self.SECTION_GENERAL, self.OPT_BACKUP)
            else:
                self.backup = False

            # Read out grouping colums
            if self.SECTION_GROUPING_FIELDS in cf.sections():
                self.groups = [i for i in cf.options(self.SECTION_GROUPING_FIELDS)]

            # Read out ignored-rows
            if self.SECTION_IGNORE in cf.sections():
                self.ignore = [i for i in cf.options(self.SECTION_IGNORE)]

            # Read out column order
            if self.SECTION_COLUMN_ORDER in cf.sections():
                self.corder = [i for i in cf.options(self.SECTION_COLUMN_ORDER)]

            # Read out component aliases
            if self.SECTION_ALIASES in cf.sections():
                self.aliases = [a.split("\t") for a in cf.options(self.SECTION_ALIASES)]

            if self.SECTION_REGEXCLUDES in cf.sections():
                self.regExcludes = []
                for pair in cf.options(self.SECTION_REGEXCLUDES):
                    if len(pair.split("\t")) == 2:
                        self.regExcludes.append(pair.split("\t"))

            if self.SECTION_REGINCLUDES in cf.sections():
                self.regIncludes = []
                for pair in cf.options(self.SECTION_REGINCLUDES):
                    if len(pair.split("\t")) == 2:
                        self.regIncludes.append(pair.split("\t"))

    # Add an option to the SECTION_GENRAL group
    def addOption(self, parser, opt, value, comment=None):
        if comment:
            if not comment.startswith(";"):
                comment = "; " + comment
            parser.set(self.SECTION_GENERAL, comment)
        parser.set(self.SECTION_GENERAL, opt, "1" if value else "0")

    # Write KiBOM preferences to file
    def Write(self, file):
        file = os.path.abspath(file)

        cf = ConfigParser.RawConfigParser(allow_no_value = True)
        cf.optionxform=str

        cf.add_section(self.SECTION_GENERAL)
        cf.set(self.SECTION_GENERAL, "; General BoM options here")
        self.addOption(cf, self.OPT_IGNORE_DNF, self.ignoreDNF, comment="If '{opt}' option is set to 1, rows that are not to be fitted on the PCB will not be written to the BoM file".format(opt=self.OPT_IGNORE_DNF))
        self.addOption(cf, self.OPT_USE_ALT, self.useAlt, comment="If '{opt}' option is set to 1, grouped references will be printed in the alternate compressed style eg: R1-R7,R18".format(opt=self.OPT_USE_ALT))
        self.addOption(cf, self.OPT_ALT_WRAP, self.altWrap, comment="If '{opt}' option is set to and integer N, the references field will wrap after N entries are printed".format(opt=self.OPT_ALT_WRAP))
        self.addOption(cf, self.OPT_NUMBER_ROWS, self.numberRows, comment="If '{opt}' option is set to 1, each row in the BoM will be prepended with an incrementing row number".format(opt=self.OPT_NUMBER_ROWS))
        self.addOption(cf, self.OPT_GROUP_CONN, self.groupConnectors, comment="If '{opt}' option is set to 1, connectors with the same footprints will be grouped together, independent of the name of the connector".format(opt=self.OPT_GROUP_CONN))
        self.addOption(cf, self.OPT_USE_REGEX, self.useRegex, comment="If '{opt}' option is set to 1, each component group will be tested against a number of regular-expressions (specified, per column, below). If any matches are found, the row is ignored in the output file".format(opt=self.OPT_USE_REGEX))
        self.addOption(cf, self.OPT_MERGE_BLANK, self.mergeBlankFields, comment="If '{opt}' option is set to 1, component groups with blank fields will be merged into the most compatible group, where possible".format(opt=self.OPT_MERGE_BLANK))
        self.addOption(cf, self.OPT_INCLUDE_VERSION, self.includeVersionNumber, comment="If '{opt}' option is set to 1, the schematic version number will be appended to the filename.")

        cf.set(self.SECTION_GENERAL, '; Field name used to determine if a particular part is to be fitted')
        cf.set(self.SECTION_GENERAL, self.OPT_CONFIG_FIELD, self.configField)

        cf.set(self.SECTION_GENERAL, '; Make a backup of the bom before generating the new one, using the folloing template')
        cf.set(self.SECTION_GENERAL, self.OPT_BACKUP, self.backup)

        cf.add_section(self.SECTION_IGNORE)
        cf.set(self.SECTION_IGNORE, "; Any column heading that appears here will be excluded from the Generated BoM")
        cf.set(self.SECTION_IGNORE, "; Titles are case-insensitive")

        for i in self.ignore:
            cf.set(self.SECTION_IGNORE, i)

        cf.add_section(self.SECTION_COLUMN_ORDER)
        cf.set(self.SECTION_COLUMN_ORDER, "; Columns will apear in the order they are listed here")
        cf.set(self.SECTION_COLUMN_ORDER, "; Titles are case-insensitive")

        for i in self.corder:
            cf.set(self.SECTION_COLUMN_ORDER, i)

        # Write the component grouping fields
        cf.add_section(self.SECTION_GROUPING_FIELDS)
        cf.set(self.SECTION_GROUPING_FIELDS, '; List of fields used for sorting individual components into groups')
        cf.set(self.SECTION_GROUPING_FIELDS, '; Components which match (comparing *all* fields) will be grouped together')
        cf.set(self.SECTION_GROUPING_FIELDS, '; Field names are case-insensitive')

        for i in self.groups:
            cf.set(self.SECTION_GROUPING_FIELDS, i)

        cf.add_section(self.SECTION_ALIASES)
        cf.set(self.SECTION_ALIASES, "; A series of values which are considered to be equivalent for the part name")
        cf.set(self.SECTION_ALIASES, "; Each line represents a tab-separated list of equivalent component name values")
        cf.set(self.SECTION_ALIASES, "; e.g. 'c c_small cap' will ensure the equivalent capacitor symbols can be grouped together")
        cf.set(self.SECTION_ALIASES, '; Aliases are case-insensitive')

        for a in self.aliases:
            cf.set(self.SECTION_ALIASES, "\t".join(a))

        cf.add_section(self.SECTION_REGINCLUDES)
        cf.set(self.SECTION_REGINCLUDES, '; A series of regular expressions used to include parts in the BoM')
        cf.set(self.SECTION_REGINCLUDES, '; If there are any regex defined here, only components that match against ANY of them will be included in the BOM')
        cf.set(self.SECTION_REGINCLUDES, '; Column names are case-insensitive')
        cf.set(self.SECTION_REGINCLUDES, '; Format is: "ColumName\tRegex" (tab-separated)')

        for i in self.regIncludes:
            if not len(i) == 2: continue
            cf.set(self.SECTION_REGINCLUDES, i[0] + "\t" + i[1])

        cf.add_section(self.SECTION_REGEXCLUDES)
        cf.set(self.SECTION_REGEXCLUDES, '; A series of regular expressions used to exclude parts from the BoM')
        cf.set(self.SECTION_REGEXCLUDES, '; If a component matches ANY of these, it will be excluded from the BoM')
        cf.set(self.SECTION_REGEXCLUDES, '; Column names are case-insensitive')
        cf.set(self.SECTION_REGEXCLUDES, '; Format is: "ColumName\tRegex" (tab-separated)')

        for i in self.regExcludes:
            if not len(i) == 2: continue

            cf.set(self.SECTION_REGEXCLUDES, i[0] + "\t" + i[1])

        with open(file, 'wb') as configfile:
            cf.write(configfile)
