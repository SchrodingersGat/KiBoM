
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
    
    OPT_IGNORE_DNF = "ignore_dnf"
    OPT_NUMBER_ROWS = "number_rows"

    def __init__(self):
        self.ignore = [
            ColumnList.COL_PART_LIB,
            ColumnList.COL_FP_LIB,
            ] #list of headings to ignore in BoM generation
        self.ignoreDNF = False #ignore rows for do-not-fit parts
        self.numberRows = True #add row-numbers to BoM output
        
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
                    self.ignoreDNF = (cf.get(self.SECTION_GENERAL, self.OPT_IGNORE_DNF) == "1")
                if cf.has_option(self.SECTION_GENERAL, self.OPT_NUMBER_ROWS):
                    self.numberRows = (cf.get(self.SECTION_GENERAL, self.OPT_NUMBER_ROWS) == "1")
                    
            #read out ignored-rows
            if self.SECTION_IGNORE in cf.sections():
                self.ignore = [i for i in cf.options(self.SECTION_IGNORE)]
            
        if verbose:
            print("Preferences:")
            print(self.OPT_IGNORE_DNF + ' = ' + str(self.ignoreDNF))
            print(self.OPT_NUMBER_ROWS + ' = ' + str(self.numberRows))
            
            for i in self.ignore:
                print("Ignoring column '" + i + "'")
            
    #write KiBOM preferences to file
    def Write(self, file):
        file = os.path.abspath(file)
        
        cf = ConfigParser.RawConfigParser(allow_no_value = True)
        
        cf.add_section(self.SECTION_GENERAL)
        cf.set(self.SECTION_GENERAL, "; General BoM options here")
        cf.set(self.SECTION_GENERAL, "; If ignore_dnf option is set to 1, rows that are not to be fitted on the PCB will not be written to the BoM file")
        cf.set(self.SECTION_GENERAL, self.OPT_IGNORE_DNF, 1 if self.ignoreDNF else 0)
        cf.set(self.SECTION_GENERAL, "; If number_rows option is set to 1, each row in the BoM will be prepended with an incrementing row number")
        cf.set(self.SECTION_GENERAL, self.OPT_NUMBER_ROWS, 1 if self.numberRows else 0)
        
        cf.add_section(self.SECTION_IGNORE)
        cf.set(self.SECTION_IGNORE, "; Any column heading that appears here will be excluded from the Generated BoM")
        cf.set(self.SECTION_IGNORE, "; Titles are case-insensitive")
        
        for i in self.ignore:
            cf.set(self.SECTION_IGNORE, i)
            
        with open(file, 'wb') as configfile:
            cf.write(configfile)