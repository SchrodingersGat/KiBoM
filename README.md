# KiBoM

[![Travis Status](https://api.travis-ci.org/SchrodingersGat/KiBoM.svg?branch=master)](https://travis-ci.org/SchrodingersGat/KiBoM)

Configurable BoM generation tool for KiCad EDA (http://kicad-pcb.org/)

## Description

KiBoM is a configurable BOM (Bill of Materials) generation tool for KiCad EDA. Written in Python, it can be used directly with KiCad software without the need for any external libraries or plugins.

KiBoM intelligently groups components based on multiple factors, and can generate BoM files in multiple output formats.

BoM options are user-configurable in a per-project configuration file.

## Usage

The *KiBOM_CLI* script can be run directly from KiCad or from the command line. For command help, run the script with the *-h* flag e.g.

`python KiBOM_CLI.py -h`

~~~~
usage: KiBOM_CLI.py [-h] [-n NUMBER] [-v] [-r VARIANT] [--cfg CFG]
                    [-s SEPARATOR]
                    netlist output

KiBOM Bill of Materials generator script

positional arguments:
  netlist               xml netlist file. Use "%I" when running from within
                        KiCad
  output                BoM output file name. Use "%O" when running from
                        within KiCad to use the default output name (csv
                        file). For e.g. HTML output, use "%O.html"

optional arguments:
  -h, --help            show this help message and exit
  -n NUMBER, --number NUMBER
                        Number of boards to build (default = 1)
  -v, --verbose         Enable verbose output
  -r VARIANT, --variant VARIANT
                        Board variant, used to determine which components are
                        output to the BoM
  --cfg CFG             BoM config file (script will try to use 'bom.ini' if
                        not specified here)
  -s SEPARATOR, --separator SEPARATOR
                        CSV Separator (default ',')


~~~~                        


**netlist** The netlist must be provided to the script. When running from KiCad use "%I"

**output** This is the path to the BoM output. When running from KiCad, usage "%O" for the default option

* If a suffix is not specified, CSV output format will be used
* HTML output can be specified within KiCad as: "%O.html" or "%O_BOM.html" (etc)
* XML output can be specified within KiCad as: "%O.xml" (etc)

**-n --number** Specify number of boards for calculating part quantities

**-v --verbose** Enable extra debugging information

**-r --variant** Specify the PCB *variant*. Support for arbitrary PCB variants allows individual components to be marked as 'fitted' or 'not fitted' in a given variant.

**--cfg** If provided, this is the BOM config file that will be used. If not provided, options will be loaded from "bom.ini"

**-s --separator** Override the delimiter for CSV or TSV generation

--------
To run from KiCad, simply add the same command line in the *Bill of Materials* script window. e.g. to generate a HTML output:

![alt tag](example/html_ex.png?raw=True "HTML Example")

## Quick Start

Download and unzip the files almost anywhere.  

When you start the KiCad schematic editor and choose *Tools>Generate Bill of Materials* expect a *Bill of Material* dialog.  Choose the *Add Plugin* button, expect a file chooser dialog.  Navigate to where you unzipped the files, select the KiBOM_CLI.py file, and choose the *Open* button.  Expect another confirmation dialog and choose *OK*.  Expect the *Command Line:* text box to be filled in, and for a description of the plugin to appear in the *Plugin Info* text box.  Choose the *Generate* button.  Expect some messages in the *Plugin Info* text box, and for a .csv file to exist in your KiCad project directory.

If you want other than .csv format, edit the *Command Line*, for example inserting ".html" after the "%O".

If you want more columns in your BOM, before you generate your BOM, in the schematic editor choose *Preferences>Schematic Editor Options*  and create new rows in the *Template Field Names* tab.  Then edit your components and fill in the fields.  KiBOM will reasonably sum rows in the BOM having the same values in your fields.  For example, if you have two components both with Vendor=Digikey and SKU=877-5309 (and value and footprints equal), there will be one row with Quantity "2" and References e.g. "R1, R2."

## Features

### Intelligent Component Grouping

To be useful for ordering components, the BoM output from a KiCad project should be organized into sensible component groups. By default, KiBom groups components based on the following factors:

* Part name: (e.g. 'R' for resistors, 'C' for capacitors, or longer part names such as 'MAX232') *note: parts such as {'R','r_small'} (which are different symbol representations for the same component) can also be grouped together*
* Value: Components must have the same value to be grouped together
* Footprint: Components must have the same footprint to be grouped together *(this option can be enabled/disabled in the bom.ini configuration file)*

#### Custom Column Grouping

If the user wishes to group components based on additional field values, these can be specified in the preferences (.ini) file

### Intelligent Value Matching

Some component values can be expressed in multiple ways (e.g. "0.1uF" === "100n" for a capacitor). KiBoM matches value strings based on their interpreted numerical value, such that components are grouped together even if their values are expressed differently.

### Field Extraction

In addition to the default KiCad fields which are assigned to each component, KiBoM extracts and custom fields added to the various components.

**Default Fields**

The following default fields are extracted and can be added to the output BoM file:
* `Description` : Part description as per the schematic symbol
* `References` : List of part references included in a particular group
* `Quantity` : Number of components included in a particular group
* `Part` : Part name as per the schematic symbol
* `Part Lib` : Part library for the symbol *(default - not output to BoM file)*
* `Footprint` : Part footprint
* `Footprint Lib` : Part footprint library *(default - not output to BoM file)*
* `Datasheet` : Component datasheet extracted either from user-included data, or from part library

**User Fields**

If any components have custom fields added, these are available to the output BoM file.

### Multiple PCB Configurations

KiBoM allows for arbitrary PCB configurations, which means that the user can specify that individual components will be included or excluded from the BoM in certain circumstances.

The preferences (.ini) file provides the *fit_field* option which designates a particular part field (default = "Config") which the user can specify whether or not a part is to be included.

**DNF Parts**

To specify a part as DNF (do not fit), the *fit_field* field can be set to one of the following values: (case insensitive)

* "dnf"
* "do not fit"
* "nofit"
* "no stuff"
* "nostuff"
* "noload"
* "do not load"

**Note:**

If the *Value* field for the component contains any of these values, the component will also not be included

**PCB Variants**

To generate a BoM with a custom *Variant*, the --variant flag can be used at the command line to specify which variant is to be used.

If a variant is specified, the value of the *fit_field* field is used to determine if a component will be included in the BoM, as follows:

* If the *fit_field* value is empty / blank then it will be loaded in ALL variants.
* If the *fit_field* begins with a '-' character, if will be excluded from the matching variant.
* If the *fit_field* begins with a '+' character, if will ONLY be included in the matching variant.

Multiple variants can be addressed as the *fit_field* can contain multiple comma-separated values.

e.g. if we have a PCB with three components that have the following values in the *fit_field* field:

* C1 -> "-production"
* C2 -> "+production"
* R1 -> ""

If the script is run with the flag *--variant production* then C2 and R1 will be loaded.

If the script is run without the *--variant production* flag, then C1 and R1 will be loaded

### Regular Expression Matching

KiBoM features two types of regex matching : "Include" and "Exclude" (each of these are specified within the preferences (bom.ini) file).

If the user wishes to include ONLY parts that match one-of-many regular expressions, these can be specified in REGEX_INCLUDE section of the bom.ini file

If the user wishes to exclude components based on one-of-many regular expressions, these are specified in the REGEX_EXCLUDE section of the bom.ini file

(Refer to the default bom.ini file for examples)

### Multiple File Outputs
Multiple BoM output formats are supported:
* CSV (Comma separated values)
* TSV (Tab separated values)
* TXT (Text file output with tab separated values)
* XML
* HTML

Output file format selection is set by the output filename. e.g. "bom.html" will be written to a HTML file, "bom.csv" will be written to a CSV file.

### Configuration File
BoM generation options can be configured (on a per-project basis) by editing the *bom.ini* file in the PCB project directory. This file is generated the first time that the KiBoM script is run, and allows configuration of the following options.
* `ignore_dnf` : Component groups designated as 'DNF' (do not fit) will be excluded from the BoM output
* `number_rows` : Add row numbers to the BoM output
* `group_connectors` : If this option is set, connector comparison based on the 'Value' field is ignored. This allows multiple connectors which are named for their function (e.g. "Power", "ICP" etc) can be grouped together.
* `test_regex` : If this option is set, each component group row is test against a list of (user configurable) regular expressions. If any matches are found, that row is excluded from the output BoM file.
* `merge_blank_field` : If this option is set, blank fields are able to be merged with non-blank fields (and do not count as a 'conflict')
* `fit_field` : This is the name of the part field used to determine if the component is fitted, or not.
* `include_version_number` : If this option is set, the schematic version number will be appended to the BOM filename (before the extension). e.g. `PRJBOM.csv` will become `PRJBOM_REV.csv`

* `IGNORE_COLUMNS` : A list of columns can be marked as 'ignore', and will not be output to the BoM file. By default, the *Part_Lib* and *Footprint_Lib* columns are ignored.
* `GROUP_FIELDS` : A list of component fields used to group components together.
* `COMPONENT_ALIASES` : A list of space-separated values which allows multiple schematic symbol visualisations to be consolidated.
* `REGEX_INCLUDE` : A list of regular expressions used to explicitly include components. If there are no regex here, all components pass this test. If there are regex here, then a component must match at least one of them to be included in the BoM.
* `REGEX_EXCLUDE` : If a component matches any of these regular expressions, it will *not* be included in the BoM.

Example configuration file (.ini format) *default values shown*

~~~~
[BOM_OPTIONS]
; General BoM options here
; If 'ignore_dnf' option is set to 1, rows that are not to be fitted on the PCB will not be written to the BoM file
ignore_dnf = 1
; If 'number_rows' option is set to 1, each row in the BoM will be prepended with an incrementing row number
number_rows = 1
; If 'group_connectors' option is set to 1, connectors with the same footprints will be grouped together, independent of the name of the connector
group_connectors = 1
; If 'test_regex' option is set to 1, each component group will be tested against a number of regular-expressions (specified, per column, below). If any matches are found, the row is ignored in the output file
test_regex = 1
; If 'merge_blank_fields' option is set to 1, component groups with blank fields will be merged into the most compatible group, where possible
merge_blank_fields = 1
; Field name used to determine if a particular part is to be fitted
fit_field = Config

[IGNORE_COLUMNS]
; Any column heading that appears here will be excluded from the Generated BoM
; Titles are case-insensitive
Part Lib
Footprint Lib

[GROUP_FIELDS]
; List of fields used for sorting individual components into groups
; Components which match (comparing *all* fields) will be grouped together
; Field names are case-insensitive
Part
Part Lib
Value
Footprint
Footprint Lib

[COMPONENT_ALIASES]
; A series of values which are considered to be equivalent for the part name
; Each line represents a tab-separated list of equivalent component name values
; e.g. 'c c_small cap' will ensure the equivalent capacitor symbols can be grouped together
; Aliases are case-insensitive
c	c_small	cap	capacitor
r	r_small	res	resistor
sw	switch
l	l_small	inductor
zener	zenersmall
d	diode	d_small

[REGEX_INCLUDE]
; A series of regular expressions used to include parts in the BoM
; If there are any regex defined here, only components that match against ANY of them will be included in the BOM
; Column names are case-insensitive
; Format is: "ColumName	Regex" (tab-separated)

[REGEX_EXCLUDE]
; A series of regular expressions used to exclude parts from the BoM
; If a component matches ANY of these, it will be excluded from the BoM
; Column names are case-insensitive
; Format is: "ColumName	Regex" (tab-separated)
References	^TP[0-9]*
References	^FID
Part	mount.*hole
Part	solder.*bridge
Part	test.*point
Footprint	test.*point
Footprint	mount.*hole
Footprint	fiducial
~~~~

## Example

A simple schematic is shown below. Here a number of resistors, capacitors, and one IC have been added to demonstrate the BoM output capability. Some of the components have custom fields added ('Vendor', 'Rating', 'Notes')

![alt tag](example/schem.png?raw=True "Schematic")

Here, a number of logical groups can be seen:

**R1 R2**
Resistors R1 and R2 have the same value (470 Ohm) even though the value is expressed differently.
Resistors R1 and R2 have the same footprint

**R3 R4**
Resistors R3 and R4 have the same value and the same footprint

**R5**
While R5 has the same value as R3 and R4, it is in a different footprint and thus cannot be placed in the same group.

**C1 C2**
C1 and C2 have the same value and footprint

**C3 C5**
C3 and C5 have the same value and footprint

**C4**
C4 has a different footprint to C3 and C5, and thus is grouped separately

A HTML BoM file is generated as follows:

![alt tag](example/bom.png?raw=True "BoM")

To add the BoM script, the Command Line options should be configured as follows:
* path-to-python-script (KiBOM_CLI.py)
* netlist-file "%I"
* output_path "%O_bom.html" (replace file extension for different output file formats)

Hit the "Generate" button, and the output window should show that the BoM generation was successful.

### HTML Output
The output HTML file is generated as follows:

![alt tag](example/html_ex.png?raw=True "HTML Gen")

![alt tag](example/html.png?raw=True "HTML Output")

Here the components are correctly grouped, with links to datasheets where appropriate, and fields color-coded.

### CSV Output
A CSV file output can be generated simply by changing the file extension

    Component,Description,Part,References,Value,Footprint,Quantity,Datasheet,Rating,Vendor,Notes
    1,Unpolarized capacitor,C,C1 C2,0.1uF,C_0805,2,,,,
    2,Unpolarized capacitor,C,C3 C5,2.2uF,C_0805,2,,,,
    3,Unpolarized capacitor,C,C4,2.2uF,C_0603,1,,100V X7R,,
    4,"Connector, single row, 01x09",CONN_01X09,P2,Comms,JST_XH_S09B-XH-A_09x2.50mm_Angled,1,,,,
    5,"Connector, single row, 01x09",CONN_01X09,P1,Power,JST_XH_S09B-XH-A_09x2.50mm_Angled,1,,,,
    6,Resistor,R,R3 R4,100,R_0805,2,,,,
    7,Resistor,R,R5,100,R_0603,1,,0.5W 0.5%,,
    8,Resistor,R,R1 R2,470R,R_0805,2,,,Digikey,
    9,"Dual RS232 driver/receiver, 5V supply, 120kb/s, 0C-70C",MAX232,U1,MAX232,DIP-16_W7.62mm,1 (DNF),http://www.ti.com/lit/ds/symlink/max232.pdf,,,Do not fit

    Component Count:,13
    Component Groups:,9
    Schematic Version:,A.1
    Schematic Date:,2016-05-15
    BoM Date:,15-May-16 5:27:07 PM
    Schematic Source:,C:/bom_test/Bom_Test.sch
    KiCad Version:,"Eeschema (2016-05-06 BZR 6776, Git 63decd7)-product"

### XML Output
An XML file output can be generated simply by changing the file extension

    <?xml version="1.0" ?>
    <KiCad_BOM BOM_Date="14-Jan-18 5:27:03 PM" KiCad_Version="Eeschema (2016-05-06 BZR 6776, Git 63decd7)-product" Schematic_Date="2016-05-15" Schematic_Source="C:/bom_test/Bom_Test.sch" Schematic_Version="A.1" components="13" groups="9">
        <group Datasheet="" Description="Unpolarized capacitor" Footprint="C_0805" Notes="" Part="C" Quantity="2" Rating="" References="C1 C2" Value="0.1uF" Vendor=""/>
        <group Datasheet="" Description="Unpolarized capacitor" Footprint="C_0805" Notes="" Part="C" Quantity="2" Rating="" References="C3 C5" Value="2.2uF" Vendor=""/>
        <group Datasheet="" Description="Unpolarized capacitor" Footprint="C_0603" Notes="" Part="C" Quantity="1" Rating="100V X7R" References="C4" Value="2.2uF" Vendor=""/>
        <group Datasheet="" Description="Connector, single row, 01x09" Footprint="JST_XH_S09B-XH-A_09x2.50mm_Angled" Notes="" Part="CONN_01X09" Quantity="1" Rating="" References="P2" Value="Comms" Vendor=""/>
        <group Datasheet="" Description="Connector, single row, 01x09" Footprint="JST_XH_S09B-XH-A_09x2.50mm_Angled" Notes="" Part="CONN_01X09" Quantity="1" Rating="" References="P1" Value="Power" Vendor=""/>
        <group Datasheet="" Description="Resistor" Footprint="R_0805" Notes="" Part="R" Quantity="2" Rating="" References="R3 R4" Value="100" Vendor=""/>
        <group Datasheet="" Description="Resistor" Footprint="R_0603" Notes="" Part="R" Quantity="1" Rating="0.5W 0.5%" References="R5" Value="100" Vendor=""/>
        <group Datasheet="" Description="Resistor" Footprint="R_0805" Notes="" Part="R" Quantity="2" Rating="" References="R1 R2" Value="470R" Vendor="Digikey"/>
        <group Datasheet="http://www.ti.com/lit/ds/symlink/max232.pdf" Description="Dual RS232 driver/receiver, 5V supply, 120kb/s, 0C-70C" Footprint="DIP-16_W7.62mm" Notes="Do not fit" Part="MAX232" Quantity="1 (DNF)" Rating="" References="U1" Value="MAX232" Vendor=""/>
    </KiCad_BOM>

## Contributors

With thanks to the following contributors:

* https://github.com/bootchk
* https://github.com/diegoherranz
* https://github.com/kylemanna
* https://github.com/pointhi
* https://github.com/schneidersoft
* https://github.com/suzizecat
