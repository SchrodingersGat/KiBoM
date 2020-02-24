# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import re
import os

from bomlib.columns import ColumnList

# Check python version to determine which version of ConfirParser to import
if sys.version_info.major >= 3:
    import configparser as ConfigParser
else:
    import ConfigParser


class BomPref:

    SECTION_IGNORE = "IGNORE_COLUMNS"
    SECTION_COLUMN_ORDER = "COLUMN_ORDER"
    SECTION_GENERAL = "BOM_OPTIONS"
    SECTION_ALIASES = "COMPONENT_ALIASES"
    SECTION_GROUPING_FIELDS = "GROUP_FIELDS"
    SECTION_REGEXCLUDES = "REGEX_EXCLUDE"
    SECTION_REGINCLUDES = "REGEX_INCLUDE"
    SECTION_DATABASE = "DATABASE"
    SECTION_DATABASE_QUERIES = "DATABASE_QUERIES"

    OPT_PCB_CONFIG = "pcb_configuration"
    OPT_NUMBER_ROWS = "number_rows"
    OPT_GROUP_CONN = "group_connectors"
    OPT_USE_REGEX = "test_regex"
    OPT_USE_ALT = "use_alt"
    OPT_ALT_WRAP = "alt_wrap"
    OPT_MERGE_BLANK = "merge_blank_fields"
    OPT_IGNORE_DNF = "ignore_dnf"
    OPT_BACKUP = "make_backup"
    OPT_OUTPUT_FILE_NAME = "output_file_name"
    OPT_VARIANT_FILE_NAME_FORMAT = "variant_file_name_format"
    OPT_DEFAULT_BOARDS = "number_boards"
    OPT_DEFAULT_PCBCONFIG = "board_variant"
    OPT_CONFIG_FIELD = "fit_field"
    OPT_HIDE_HEADERS = "hide_headers"
    OPT_HIDE_PCB_INFO = "hide_pcb_info"
    OPT_DB_HOST = "host"
    OPT_DB_USER = "user"
    OPT_DB_PASSWORD = "password"
    OPT_DB_DB = "database"

    def __init__(self):
        # List of headings to ignore in BoM generation
        self.ignore = [
            ColumnList.COL_PART_LIB,
            ColumnList.COL_FP_LIB,
        ]

        self.corder = ColumnList._COLUMNS_DEFAULT
        self.useAlt = False  # Use alternate reference representation
        self.altWrap = None  # Wrap to n items when using alt representation
        self.ignoreDNF = True  # Ignore rows for do-not-fit parts
        self.numberRows = True  # Add row-numbers to BoM output
        self.groupConnectors = True  # Group connectors and ignore component value
        self.useRegex = True  # Test various columns with regex

        self.boards = 1  # Quantity of boards to be made
        self.mergeBlankFields = True  # Blanks fields will be merged when possible
        self.hideHeaders = False
        self.hidePcbInfo = False
        self.verbose = False  # By default, is not verbose
        self.configField = "Config"  # Default field used for part fitting config
        self.pcbConfig = ["default"]

        self.backup = "%O.tmp"

        self.separatorCSV = None
        self.outputFileName = "%O_bom_%v%V"
        self.variantFileNameFormat = "_(%V)"

        self.xlsxwriter_available = False
        self.xlsxwriter2_available = False

        self.mysql_available = False

        self.db_host = ""
        self.db_user = ""
        self.db_pass = ""
        self.db_db = ""
        self.db_cnx = None
        self.db_cursor = None
        self.db_queries = []

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
            [ColumnList.COL_REFERENCE, '^TP[0-9]*'],
            [ColumnList.COL_REFERENCE, '^FID'],
            [ColumnList.COL_PART, 'mount.*hole'],
            [ColumnList.COL_PART, 'solder.*bridge'],
            [ColumnList.COL_PART, 'test.*point'],
            [ColumnList.COL_FP, 'test.*point'],
            [ColumnList.COL_FP, 'mount.*hole'],
            [ColumnList.COL_FP, 'fiducial'],
        ]

        # Default component groupings
        self.aliases = [
            ["c", "c_small", "cap", "capacitor"],
            ["r", "r_small", "res", "resistor"],
            ["sw", "switch"],
            ["l", "l_small", "inductor"],
            ["zener", "zenersmall"],
            ["d", "diode", "d_small"]
        ]

    # Check an option within the SECTION_GENERAL group
    def checkOption(self, parser, opt, default=False):
        if parser.has_option(self.SECTION_GENERAL, opt):
            return parser.get(self.SECTION_GENERAL, opt).lower() in ["1", "true", "yes"]
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

        cf = ConfigParser.RawConfigParser(allow_no_value=True)
        cf.optionxform = str

        cf.read(file)

        # Read general options
        if self.SECTION_GENERAL in cf.sections():
            self.ignoreDNF = self.checkOption(cf, self.OPT_IGNORE_DNF, default=True)
            self.useAlt = self.checkOption(cf, self.OPT_USE_ALT, default=False)
            self.altWrap = self.checkInt(cf, self.OPT_ALT_WRAP, default=None)
            self.numberRows = self.checkOption(cf, self.OPT_NUMBER_ROWS, default=True)
            self.groupConnectors = self.checkOption(cf, self.OPT_GROUP_CONN, default=True)
            self.useRegex = self.checkOption(cf, self.OPT_USE_REGEX, default=True)
            self.mergeBlankFields = self.checkOption(cf, self.OPT_MERGE_BLANK, default=True)
            self.outputFileName = cf.get(self.SECTION_GENERAL, self.OPT_OUTPUT_FILE_NAME)
            self.variantFileNameFormat = cf.get(self.SECTION_GENERAL, self.OPT_VARIANT_FILE_NAME_FORMAT)

        if cf.has_option(self.SECTION_GENERAL, self.OPT_CONFIG_FIELD):
            self.configField = cf.get(self.SECTION_GENERAL, self.OPT_CONFIG_FIELD)

        if cf.has_option(self.SECTION_GENERAL, self.OPT_DEFAULT_BOARDS):
            self.boards = self.checkInt(cf, self.OPT_DEFAULT_BOARDS, default=None)

        if cf.has_option(self.SECTION_GENERAL, self.OPT_DEFAULT_PCBCONFIG):
            self.pcbConfig = cf.get(self.SECTION_GENERAL, self.OPT_DEFAULT_PCBCONFIG).strip().split(",")

        if cf.has_option(self.SECTION_GENERAL, self.OPT_BACKUP):
            self.backup = cf.get(self.SECTION_GENERAL, self.OPT_BACKUP)
        else:
            self.backup = False

        if cf.has_option(self.SECTION_GENERAL, self.OPT_HIDE_HEADERS):
            self.hideHeaders = cf.get(self.SECTION_GENERAL, self.OPT_HIDE_HEADERS) == '1'

        if cf.has_option(self.SECTION_GENERAL, self.OPT_HIDE_PCB_INFO):
            self.hidePcbInfo = cf.get(self.SECTION_GENERAL, self.OPT_HIDE_PCB_INFO) == '1'

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
            self.aliases = [re.split('[ \t]+', a) for a in cf.options(self.SECTION_ALIASES)]

        if self.SECTION_REGEXCLUDES in cf.sections():
            self.regExcludes = []
            for pair in cf.options(self.SECTION_REGEXCLUDES):
                if len(re.split('[ \t]+', pair)) == 2:
                    self.regExcludes.append(re.split('[ \t]+', pair))

        if self.SECTION_REGINCLUDES in cf.sections():
            self.regIncludes = []
            for pair in cf.options(self.SECTION_REGINCLUDES):
                if len(re.split('[ \t]+', pair)) == 2:
                    self.regIncludes.append(re.split('[ \t]+', pair))

        if self.SECTION_DATABASE in cf.sections():
            if cf.has_option(self.SECTION_DATABASE, self.OPT_DB_HOST):
                self.db_host = cf.get(self.SECTION_DATABASE, self.OPT_DB_HOST)
            if cf.has_option(self.SECTION_DATABASE, self.OPT_DB_USER):
                self.db_user = cf.get(self.SECTION_DATABASE, self.OPT_DB_USER)
            if cf.has_option(self.SECTION_DATABASE, self.OPT_DB_PASSWORD):
                self.db_pass = cf.get(self.SECTION_DATABASE, self.OPT_DB_PASSWORD)
            if cf.has_option(self.SECTION_DATABASE, self.OPT_DB_DB):
                self.db_db = cf.get(self.SECTION_DATABASE, self.OPT_DB_DB)

        if self.SECTION_DATABASE_QUERIES in cf.sections():
            self.regExcludes = []
            for pair in cf.options(self.SECTION_DATABASE_QUERIES):
                #if len(re.split('[ \t]+', pair)) == 2:
                    self.db_queries.append(re.split('[ \t]+', pair))

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

        cf = ConfigParser.RawConfigParser(allow_no_value=True)
        cf.optionxform = str

        cf.add_section(self.SECTION_GENERAL)
        cf.set(self.SECTION_GENERAL, "; General BoM options here")
        self.addOption(cf, self.OPT_IGNORE_DNF, self.ignoreDNF, comment="If '{opt}' option is set to 1, rows that are not to be fitted on the PCB will not be written to the BoM file".format(opt=self.OPT_IGNORE_DNF))
        self.addOption(cf, self.OPT_USE_ALT, self.useAlt, comment="If '{opt}' option is set to 1, grouped references will be printed in the alternate compressed style eg: R1-R7,R18".format(opt=self.OPT_USE_ALT))
        self.addOption(cf, self.OPT_ALT_WRAP, self.altWrap, comment="If '{opt}' option is set to and integer N, the references field will wrap after N entries are printed".format(opt=self.OPT_ALT_WRAP))
        self.addOption(cf, self.OPT_NUMBER_ROWS, self.numberRows, comment="If '{opt}' option is set to 1, each row in the BoM will be prepended with an incrementing row number".format(opt=self.OPT_NUMBER_ROWS))
        self.addOption(cf, self.OPT_GROUP_CONN, self.groupConnectors, comment="If '{opt}' option is set to 1, connectors with the same footprints will be grouped together, independent of the name of the connector".format(opt=self.OPT_GROUP_CONN))
        self.addOption(cf, self.OPT_USE_REGEX, self.useRegex, comment="If '{opt}' option is set to 1, each component group will be tested against a number of regular-expressions (specified, per column, below). If any matches are found, the row is ignored in the output file".format(opt=self.OPT_USE_REGEX))
        self.addOption(cf, self.OPT_MERGE_BLANK, self.mergeBlankFields, comment="If '{opt}' option is set to 1, component groups with blank fields will be merged into the most compatible group, where possible".format(opt=self.OPT_MERGE_BLANK))
        
        cf.set(self.SECTION_GENERAL, "; Specify output file name format, %O is the defined output name, %v is the version, %V is the variant name which will be ammended according to 'variant_file_name_format'.")
        cf.set(self.SECTION_GENERAL, self.OPT_OUTPUT_FILE_NAME, self.outputFileName)

        cf.set(self.SECTION_GENERAL, "; Specify the variant file name format, this is a unique field as the variant is not always used/specified. When it is unused you will want to strip all of this.")
        cf.set(self.SECTION_GENERAL, self.OPT_VARIANT_FILE_NAME_FORMAT, self.variantFileNameFormat)

        cf.set(self.SECTION_GENERAL, '; Field name used to determine if a particular part is to be fitted')
        cf.set(self.SECTION_GENERAL, self.OPT_CONFIG_FIELD, self.configField)

        cf.set(self.SECTION_GENERAL, '; Make a backup of the bom before generating the new one, using the following template')
        cf.set(self.SECTION_GENERAL, self.OPT_BACKUP, self.backup)

        cf.set(self.SECTION_GENERAL, '; Default number of boards to produce if none given on CLI with -n')
        cf.set(self.SECTION_GENERAL, self.OPT_DEFAULT_BOARDS, self.boards)

        cf.set(self.SECTION_GENERAL, '; Default PCB variant if none given on CLI with -r')
        cf.set(self.SECTION_GENERAL, self.OPT_DEFAULT_PCBCONFIG, self.pcbConfig)

        cf.set(self.SECTION_GENERAL, '; Whether to hide headers from output file')
        cf.set(self.SECTION_GENERAL, self.OPT_HIDE_HEADERS, self.hideHeaders)

        cf.set(self.SECTION_GENERAL, '; Whether to hide PCB info from output file')
        cf.set(self.SECTION_GENERAL, self.OPT_HIDE_PCB_INFO, self.hidePcbInfo)

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
        cf.set(self.SECTION_ALIASES, "; Each line represents a list of equivalent component name values separated by white space")
        cf.set(self.SECTION_ALIASES, "; e.g. 'c c_small cap' will ensure the equivalent capacitor symbols can be grouped together")
        cf.set(self.SECTION_ALIASES, '; Aliases are case-insensitive')

        for a in self.aliases:
            cf.set(self.SECTION_ALIASES, "\t".join(a))

        cf.add_section(self.SECTION_REGINCLUDES)
        cf.set(self.SECTION_REGINCLUDES, '; A series of regular expressions used to include parts in the BoM')
        cf.set(self.SECTION_REGINCLUDES, '; If there are any regex defined here, only components that match against ANY of them will be included in the BOM')
        cf.set(self.SECTION_REGINCLUDES, '; Column names are case-insensitive')
        cf.set(self.SECTION_REGINCLUDES, '; Format is: "[ColumName] [Regex]" (white-space separated)')

        for i in self.regIncludes:
            if not len(i) == 2:
                continue
            cf.set(self.SECTION_REGINCLUDES, i[0] + "\t" + i[1])

        cf.add_section(self.SECTION_REGEXCLUDES)
        cf.set(self.SECTION_REGEXCLUDES, '; A series of regular expressions used to exclude parts from the BoM')
        cf.set(self.SECTION_REGEXCLUDES, '; If a component matches ANY of these, it will be excluded from the BoM')
        cf.set(self.SECTION_REGEXCLUDES, '; Column names are case-insensitive')
        cf.set(self.SECTION_REGEXCLUDES, '; Format is: "[ColumName] [Regex]" (white-space separated)')

        for i in self.regExcludes:
            if not len(i) == 2:
                continue

            cf.set(self.SECTION_REGEXCLUDES, i[0] + "\t" + i[1])

        cf.add_section(self.SECTION_DATABASE)
        cf.set(self.SECTION_DATABASE, self.OPT_DB_HOST, self.db_host )
        cf.set(self.SECTION_DATABASE, self.OPT_DB_USER, self.db_user)
        cf.set(self.SECTION_DATABASE, self.OPT_DB_PASSWORD, self.db_pass)
        cf.set(self.SECTION_DATABASE, self.OPT_DB_DATABASE, self.db_db)

        cf.add_section(self.SECTION_DATABASE_QUERIES)
        cf.set(self.SECTION_DATABASE_QUERIES, '; These database queries are called for each component.')
        cf.set(self.SECTION_DATABASE_QUERIES, '; Using these queries allows to define new fields or modify existing fields based on database data.')
        cf.set(self.SECTION_DATABASE_QUERIES, ';')
        cf.set(self.SECTION_DATABASE_QUERIES, '; Two database style queries are supported: ')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   - CALL, for executing database stored procedures,')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   - SELECT style, or any other one line query, for getting values from the database.')
        cf.set(self.SECTION_DATABASE_QUERIES, ';')
        cf.set(self.SECTION_DATABASE_QUERIES, '; Format for calling database stored procedures:')
        cf.set(self.SECTION_DATABASE_QUERIES, ';    - Name of the field. An existing field with this name is modified, or a new field with this name is created.')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |  The field\'s value is the output of the procedure.')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |  If the procedure returns several rows or values, the output is the concatenation of those values, separated by commas.   ')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |  If the field\'s name is \'None\' (without quotes, caseless), then no field is added or created.')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |     - \'CALL\' (without quotes, caseless)')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |    |           - Name of database stored procedure. ')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |    |          |           -  open parenthesis, marks beginning of arguments. Space character before and after it.')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |    |          |          |    ---------- arguments, as many as the procedure needs, separted by spaces.')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |    |          |          |   |   |    |  If an argument begins with \'$\' character, it will be evaluated before')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |    |          |          |   |   |    |  calling the procedure. For more details, see below.')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |    |          |          |   |   |    |       - close parenthesis, marks ending of arguments')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |    |          |          |   |   |    |       |')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   v    v          v          v   v   v    v       v')
        cf.set(self.SECTION_DATABASE_QUERIES, '; Field CALL Internal_procedure ( arg1 arg2 arg3 ... )')
        cf.set(self.SECTION_DATABASE_QUERIES, ';')
        cf.set(self.SECTION_DATABASE_QUERIES, '; Format for executing a database query:')
        cf.set(self.SECTION_DATABASE_QUERIES, ';    - Name of the field. An existing field with this name is modified, or a new field with this name is created.')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |  The field\'s value is the output of the query.')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |  If the query returns several rows or values, only the first one is returned.   ')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |  If the field\'s name is \'None\' (without quotes, caseless), then no field is added or created.')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |     - Database query. Each word separated by strings.')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |    |')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |    |                       ------ arguments, as many as the query needs, separted by spaces.')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |    |                      |     |   if the argument is not fixed, like arg2, put its name inside parenthesis, with \'%\' character')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |    |                      |     |   before open parenthesis. The character after close parenthesis is the type of the argument:')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |    |                      |     |   s for string, i for integer,...')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |    |                      |     |            - open curly bracket, marks beginning of arguments. Space character before and after it.')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |    |                      |     |           |  Inside the curly brackets, arguments are pairs of name and value, separated by spaces.')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |    |                      |     |           |   - name of the argument to be substituted by the following value')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |    |                      |     |           |  |      - If an argument value begins with \'$\' character, it will be evaluated before')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |    |                      |     |           |  |      |   executing the query. For more details, see below.')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |    |                      |     |           |  |      |                           - close curly bracket, marks ending of arguments')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   |    |                      |     |           |  |      |----------------|         |')
        cf.set(self.SECTION_DATABASE_QUERIES, ';   v    v                      v     v           v  v      v                v         v')
        cf.set(self.SECTION_DATABASE_QUERIES, '; Field SELECT anything LIKE ( arg1 %(arg2)s... ) { arg2 mystring arg3 $expresion      }')
        cf.set(self.SECTION_DATABASE_QUERIES, ';')
        cf.set(self.SECTION_DATABASE_QUERIES, '; Expresions to be evaluated:')
        cf.set(self.SECTION_DATABASE_QUERIES, ';')
        cf.set(self.SECTION_DATABASE_QUERIES, ';     Every argument when calling database stored procedures, or every argument value if defining queries, can be evaluated before executing the query or procedure.')
        cf.set(self.SECTION_DATABASE_QUERIES, ';     If they needs to be evaluated, their first character should be \'$\'.')
        cf.set(self.SECTION_DATABASE_QUERIES, ';     The evaluation is done by Python, so it should be Python code, and any field in the current component can be used.')
        cf.set(self.SECTION_DATABASE_QUERIES, ';     In order to do that, the object named \'component\' is the current component, and we can get any field defined for this component using, for example:')
        cf.set(self.SECTION_DATABASE_QUERIES, ';        $component.getValue()     : returns the value of the component')
        cf.set(self.SECTION_DATABASE_QUERIES, ';        $component.getFootprint() : returns the footprint of the component')
        cf.set(self.SECTION_DATABASE_QUERIES, ';        $component.getField(field_name) : returns the value for this component of field named \'name\'.')
        cf.set(self.SECTION_DATABASE_QUERIES, ';     Several fields can be combined, but there should be only one \'$\' at the beginning of the expression, and no spaces between. For example:')
        cf.set(self.SECTION_DATABASE_QUERIES, ';        $component.getValue()+'|'+component.getFootprint()   : returns a string like \'value|footprint\'')
        cf.set(self.SECTION_DATABASE_QUERIES, ';')

        with open(file, 'wb') as configfile:
            cf.write(configfile)
