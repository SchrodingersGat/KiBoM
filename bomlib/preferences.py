# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import re
import os

from bomlib.columns import ColumnList

# Check python version to determine which version of ConfigParser to import
if sys.version_info.major >= 3:
    import configparser as ConfigParser
else:
    import ConfigParser


class BomPref:

    SECTION_IGNORE = 'IGNORE_COLUMNS'
    SECTION_COLUMN_ORDER = 'COLUMN_ORDER'
    SECTION_GENERAL = 'BOM_OPTIONS'
    SECTION_ALIASES = 'COMPONENT_ALIASES'
    SECTION_GROUPING_FIELDS = 'GROUP_FIELDS'
    SECTION_REGEXCLUDES = 'REGEX_EXCLUDE'
    SECTION_REGINCLUDES = 'REGEX_INCLUDE'

    '''
    cfg_spec contains meta data about the config file.
    This information is used when parsing the contfig file to check type and set defuaults.
    each item is a touple with the following fields:

    programatic name - usually CamelCase
    section name - USUALLY_YELLING or None if not configurable
    option name - usually_snake_case of None if the option comprises of the entire section
    type - a list of types this option will accept.
        fi. ['Boolean', 'None'] for options that must be True, False or None
    default - the default to set this variable to.
        put whatever you want here
        The only requirement is that if the option is written to file; the default must be compatible with the type
    helptext - that thing that tells you what the option does.
        you can use {opt} as a placeholder fot the option name
    '''
    cfg_spec = [
        ('useAlt',           SECTION_GENERAL, 'use_alt', ['Boolean'], False,
            'If \'{opt}\' option is set to True, grouped references will be printed in the alternate compressed style eg: R1-R7,R18'),

        ('altWrap',          SECTION_GENERAL, 'alt_wrap', ['Int', 'None'], None,
            'If \'{opt}\' option is set to an integer N, the references field will wrap after N entries are printed'),

        ('agregateValues',   SECTION_GENERAL, 'agregate_values', ['Boolean'], True,
            '''If \'{opt}\' option is set to True values will be agregated as a comma seperated list.
            This is useful if you find you have multiple component with differeing values grouped together.'''),

        ('ignoreDNF',        SECTION_GENERAL, 'ignore_dnf', ['Boolean'], True,
            'If \'{opt}\' option is set to True, rows that are not to be fitted on the PCB will not be written to the BoM file'),

        ('numberRows',       SECTION_GENERAL, 'number_rows', ['Boolean'], True,
            'If \'{opt}\' option is set to True, each row in the BoM will be prepended with an incrementing row number'),

        ('groupConnectors',  SECTION_GENERAL, 'group_connectors', ['Boolean'], True,
            'If \'{opt}\' option is set to True, connectors with the same footprints will be grouped together, independent of the name of the connector'),

        ('useRegex',         SECTION_GENERAL, 'test_regex', ['Boolean'], True,
            'If \'{opt}\' option is set to True, each component group will be tested against a number of regular-expressions (specified, per column, below). If any matches are found, the row is ignored in the output file'),

        ('boards',           SECTION_GENERAL, 'number_boards', ['Int'], 1,
            'Default number of boards to produce if none given on CLI with -n'),

        ('mergeBlankFields', SECTION_GENERAL, 'merge_blank_fields', ['Boolean'], True,
            'If \'{opt}\' option is set to True, component groups with blank fields will be merged into the most compatible group, where possible'),

        ('hideHeaders',      SECTION_GENERAL, 'hide_headers', ['Boolean'], False,
            'If \'{opt}\' option is set to True, column headers will be omitted from the output file'),

        ('hidePcbInfo',      SECTION_GENERAL, 'hide_pcb_info', ['Boolean'], False,
            'Whether to hide PCB info from output file'),

        ('verbose',          None, None, ['Boolean'], False,
            ''),

        ('configField',      SECTION_GENERAL, 'fit_field', ['Str'], 'Config',
            'Field name used to determine if a particular part is to be fitted'),

        ('separatorCSV',     None, None, ['Str'], None,
            ''),

        ('backup',           SECTION_GENERAL, 'make_backup', ['Str', 'None'], '%O.tmp',
            'Make a backup of the bom before generating the new one, using the following template'),

        ('outputFileName',   SECTION_GENERAL, 'output_file_name', ['Str'], '%O_bom_%v%V',
            'Specify output file name format, %O is the defined output name, %v is the version, %V is the variant name which will be ammended according to \'variant_file_name_format\'.'),

        ('variantFileNameFormat', SECTION_GENERAL, 'variant_file_name_format', ['Str'], '_(%V)',
            'Specify the variant file name format, this is a unique field as the variant is not always used/specified. When it is unused you will want to strip all of this.'),

        ('pcbConfig', SECTION_GENERAL, 'pcb_configuration', ['Array'], ['default'],
            'Default PCB variant if none given on CLI with -r'),

        ('groups', SECTION_GROUPING_FIELDS, None, ['Array'],
            [
                ColumnList.COL_PART,
                ColumnList.COL_PART_LIB,
                ColumnList.COL_VALUE,
                ColumnList.COL_FP,
                ColumnList.COL_FP_LIB,
            ],
            '''List of fields used for sorting individual components into groups
            Components which match (comparing *all* fields) will be grouped together
            Field names are case-insensitive'''),

        ('ignore', SECTION_IGNORE, None, ['Array'],
            [
                ColumnList.COL_PART_LIB,
                ColumnList.COL_FP_LIB,
            ],
            '''Any column heading that appears here will be excluded from the Generated BoM
            Titles are case-insensitive'''),

        ('corder', SECTION_COLUMN_ORDER, None, ['Array'], ColumnList._COLUMNS_DEFAULT,
            '''Columns will apear in the order they are listed here
            Titles are case-insensitive'''),

        ('aliases', SECTION_ALIASES, None, ['Tabbed'], [
                ['c', 'c_small', 'cap', 'capacitor'],
                ['r', 'r_small', 'res', 'resistor'],
                ['sw', 'switch'],
                ['l', 'l_small', 'inductor'],
                ['zener', 'zenersmall'],
                ['d', 'diode', 'd_small']
            ],
            '''A series of values which are considered to be equivalent for the part name
            Each line represents a list of equivalent component name values separated by white space
            e.g. 'c c_small cap' will ensure the equivalent capacitor symbols can be grouped together
            Aliases are case-insensitive'''),

        ('regExcludes', SECTION_REGEXCLUDES, None, ['Regex'], [
                [ColumnList.COL_REFERENCE, '^TP[0-9]*'],
                [ColumnList.COL_REFERENCE, '^FID'],
                [ColumnList.COL_PART, 'mount.*hole'],
                [ColumnList.COL_PART, 'solder.*bridge'],
                [ColumnList.COL_PART, 'test.*point'],
                [ColumnList.COL_FP, 'test.*point'],
                [ColumnList.COL_FP, 'mount.*hole'],
                [ColumnList.COL_FP, 'fiducial'],
            ],
            '''A series of regular expressions used to exclude parts from the BoM
            If a component matches ANY of these, it will be excluded from the BoM
            Column names are case-insensitive
            Format is: \'[ColumName] [Regex]\' (white-space separated)'''),

        ('regIncludes', SECTION_REGINCLUDES, None, ['Regex'], [],
            '''A series of regular expressions used to include parts in the BoM
            If there are any regex defined here, only components that match against ANY of them will be included in the BOM
            Column names are case-insensitive
            Format is: \'[ColumName] [Regex]\' (white-space separated)'''),
    ]

    def __init__(self):
        # set defaults from spec
        for row in self.cfg_spec:
            prgname = row[0]
            default = row[4]
            setattr(self, prgname, default)

        # cruft for feature detection (default disabled)
        self.xlsxwriter_available = False
        self.xlsxwriter2_available = False

    # Read KiBOM preferences from file
    def Read(self, file, verbose=False):
        file = os.path.abspath(file)
        if not os.path.exists(file) or not os.path.isfile(file):
            print('{f} is not a valid file!'.format(f=file))
            return

        cf = ConfigParser.RawConfigParser(allow_no_value=True)
        cf.optionxform = str
        cf.read(file)

        for row in self.cfg_spec:
            prgname = row[0]
            section = row[1]
            optname = row[2]
            vartype = row[3]
            default = row[4]
            hlptext = row[5]

            # skip stuff not allowed in a config file
            if section is None and optname is None:
                continue

            # skip loading stuff not in the config file
            if section not in cf.sections():
                continue

            if optname is None:
                # this option is comprised of the entire section

                if 'Array' in vartype:
                    vals = [i for i in cf.options(section)]
                    setattr(self, prgname, vals)

                elif 'Tabbed' in vartype:
                    vals = [re.split('[ \t]+', a) for a in cf.options(section)]
                    setattr(self, prgname, vals)

                elif 'Regex' in vartype:
                    vals = []
                    for pair in cf.options(section):
                        if len(re.split('[ \t]+', pair)) == 2:
                            vals.append(re.split('[ \t]+', pair))
                    setattr(self, prgname, vals)
                else:
                    raise NameError('unsupported option type `{}` specified in cfg (init) spec'.format(vartype))
            else:
                # this is normal option

                if not cf.has_option(section, optname): # leave defaults if not overiden
                    continue

                val = cf.get(section, optname)

                if 'None' in vartype and val is None:
                    setattr(self, prgname, None)
                elif 'Boolean' in vartype and str(val).lower() in ['true', '1', 'yes', 'ja']:
                    setattr(self, prgname, True)
                elif 'Boolean' in vartype and str(val).lower() in ['false', '0', 'no', 'nein']:
                    setattr(self, prgname, False)
                elif 'Int' in vartype:
                    setattr(self, prgname, int(val))
                elif 'Str' in vartype:
                    setattr(self, prgname, str(val))
                elif 'Array' in vartype:
                    setattr(self, prgname, str(val).strip().split(','))
                else:
                    raise NameError('unsupported option type `{}` specified in cfg (init) spec'.format(vartype))

    # Write KiBOM preferences to file
    def Write(self, file):
        file = os.path.abspath(file)

        cf = ConfigParser.RawConfigParser(allow_no_value=True)
        cf.optionxform = str

        already_defined = []
        for row in self.cfg_spec:
            prgname = row[0]
            section = row[1]
            optname = row[2]
            vartype = row[3]
            default = row[4]
            hlptext = row[5]

            if section is None:
                continue;

            if section not in already_defined:
                cf.add_section(section)
                already_defined.append(section)

            for hlp in hlptext.format(opt=optname).split('\n'):
                cf.set(section, '; {}'.format(hlp.strip()))

            if optname is None:
                if 'Array' in vartype:
                    for i in getattr(self, prgname):
                        cf.set(section, i)

                elif 'Tabbed' in vartype:
                    for i in getattr(self, prgname):
                        cf.set(section, '\t'.join(i))

                elif 'Regex' in vartype:
                    for i in getattr(self, prgname):
                        cf.set(section, '\t'.join(i))
                else:
                    raise NameError('unsupported option type `{}` specified in cfg (init) spec'.format(vartype))
            else:
                if 'Array' in vartype:
                    cf.set(section, optname, ','.join(getattr(self, prgname)))
                else:
                    val = getattr(self, prgname)
                    if val is None:
                        cf.set(section, '; {} = {}'.format(optname, default))
                    else:
                        cf.set(section, optname, val)

        with open(file, 'wb') as configfile:
            cf.write(configfile)

