# KiBoM
Configurable BoM generation tool for KiCad EDA (http://kicad-pcb.org/)

## Description

KiBoM is a configurable BOM (Bill of Materials) generation tool for KiCad EDA. Written in Python, it can be used directly with KiCad software without the need for any external libraries or plugins. 

KiBoM intelligently groups components based on multiple factors, and can generate BoM files in multiple output formats.

BoM options are user-configurable in a per-project configuration file.

## Usage

The *KiBOM_CLI* script can be run directly from KiCad or from the command line. For command help, run the script with the *-h* flag e.g. 

    python KiBOM_CLI.py -h
    
![alt tag](example/usage.png?raw=True "Command Line")

**netlist** The netlist must be provided to the script. When running from KiCAD use "%I"

**output** This is the path to the BoM output. When running from KiCad, usage "%O" for the default option

* If a suffix is not specified, CSV output format will be used
* HTML output can be specified within KiCad as: "%O.html" or "%O_BOM.html" (etc)
* XML output can be specified within KiCad as: "%O.xml" (etc)

**-b --boards** Specify number of boards for calculating part quantities

**-v --verbose** Enable extra debugging information

**-n --noheader** Do not generate extra header information within the file. (HTML and CSV output only)

**--cfg** If provided, this is the BOM config file that will be used. If not provided, options will be loaded from "bom.ini"


To run from KiCad, simply add the same command line in the *Bill of Materials* script window. e.g. to generate a HTML output:

![alt tag](example/html_eg.png?raw=True "HTML Example")

## Features

### Intelligent Component Grouping

To be useful for ordering components, the BoM output from a KiCad project should be organized into sensible component groups. KiBom groups components based on the following factors:

* Part name: (e.g. 'R' for resistors, 'C' for capacitors, or longer part names such as 'MAX232') *note: parts such as {'R','r_small'} (which are different symbol representations for the same component) can also be grouped together*
* Value: Components must have the same value to be grouped together 
* Footprint: Components must have the same footprint to be grouped together *(this option can be enabled/disabled in the bom.ini configuration file)*

### Intelligent Value Matching

Some component values can be expressed in multiple ways (e.g. "0.1uF" === "100n" for a capacitor). KiBoM matches value strings based on their interpreted numerical value, such that components are grouped together even if their values are expressed differenly.

### Field Extraction

In addition to the default KiCad fields which are assigned to each component, KiBoM extracts and custom fields added to the various components. 

**Default Fields**
The following default fields are extracted and can be added to the output BoM file:
* Description - Part description as per the schematic symbol
* References - List of part references included in a particular group
* Quantity - Number of components included in a particular group
* Part - Part name as per the schematic symbol
* Part Lib - Part library for the symbol *(default - not output to BoM file)*
* Footprint - Part footprint
* Footprint Lib - Part footprint library *(default - not output to BoM file)*
* Datasheet - Component datasheet extracted either from user-included data, or from part library

**User Fields**
If any components have custom fields added, these are available to the output BoM file.

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
* *ignore_dnf*: Component groups marked as 'DNF' (do not fit) will be excluded from the BoM output
* *number_rows*: Add row numbers to the BoM output
* *group_connectors*: If this option is set, connector comparison based on the 'Value' field is ignored. This allows multiple connectors which are named for their function (e.g. "Power", "ICP" etc) can be grouped together.
* *test_regex*: If this option is set, each component group row is test against a list of (user configurable) regular expressions. If any matches are found, that row is excluded from the output BoM file.
* *compare_footprints*: If this option is set *(default)*, two components must have the same footprint to be grouped together. If not set, components with different footprints can be grouped together

* *IGNORE_COLUMNS*: A list of columns can be marked as 'ignore', and will not be output to the BoM file. By default, the *Part_Lib* and *Footprint_Lib* columns are ignored.
* *COMPONENT_ALIASES*: A list of space-separated values which allows multiple schematic symbol visualisations to be consolidated.
* *REGEXCLUDE_COLUMN_NAME*: A list of regular expressions to ignore components based on the value in a given column.

Example configuration file (.ini format) *default values shown*
![alt tag](example/ini.png?raw=True "Configuration")

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

**C3 C4**
C3 and C4 have the same value and footprint

**C5**
C5 has a different footprint to C3 and C4, and thus is grouped separately

A HTML BoM file is generated as follows:

![alt tag](example/bom.png?raw=True "BoM")

To add the BoM script, the Command Line options should be configured as follows:
* path-to-python-script (KiBOM_CLI.py)
* netlist-file "%I"
* output_path "%O_bom.html" (replace file extension for different output file formats)

Hit the "Generate" button, and the output window should show that the BoM generation was successful.

### HTML Output
The output HTML file is generated as follows:

![alt tag](example/html_eg.png?raw=True "HTML Gen")

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
    <KiCAD_BOM BOM_Date="15-May-16 5:27:03 PM" KiCad_Version="Eeschema (2016-05-06 BZR 6776, Git 63decd7)-product" Schematic_Date="2016-05-15" Schematic_Source="C:/bom_test/Bom_Test.sch" Schematic_Version="A.1" components="13" groups="9">
        <group Datasheet="" Description="Unpolarized capacitor" Footprint="C_0805" Notes="" Part="C" Quantity="2" Rating="" References="C1 C2" Value="0.1uF" Vendor=""/>
        <group Datasheet="" Description="Unpolarized capacitor" Footprint="C_0805" Notes="" Part="C" Quantity="2" Rating="" References="C3 C5" Value="2.2uF" Vendor=""/>
        <group Datasheet="" Description="Unpolarized capacitor" Footprint="C_0603" Notes="" Part="C" Quantity="1" Rating="100V X7R" References="C4" Value="2.2uF" Vendor=""/>
        <group Datasheet="" Description="Connector, single row, 01x09" Footprint="JST_XH_S09B-XH-A_09x2.50mm_Angled" Notes="" Part="CONN_01X09" Quantity="1" Rating="" References="P2" Value="Comms" Vendor=""/>
        <group Datasheet="" Description="Connector, single row, 01x09" Footprint="JST_XH_S09B-XH-A_09x2.50mm_Angled" Notes="" Part="CONN_01X09" Quantity="1" Rating="" References="P1" Value="Power" Vendor=""/>
        <group Datasheet="" Description="Resistor" Footprint="R_0805" Notes="" Part="R" Quantity="2" Rating="" References="R3 R4" Value="100" Vendor=""/>
        <group Datasheet="" Description="Resistor" Footprint="R_0603" Notes="" Part="R" Quantity="1" Rating="0.5W 0.5%" References="R5" Value="100" Vendor=""/>
        <group Datasheet="" Description="Resistor" Footprint="R_0805" Notes="" Part="R" Quantity="2" Rating="" References="R1 R2" Value="470R" Vendor="Digikey"/>
        <group Datasheet="http://www.ti.com/lit/ds/symlink/max232.pdf" Description="Dual RS232 driver/receiver, 5V supply, 120kb/s, 0C-70C" Footprint="DIP-16_W7.62mm" Notes="Do not fit" Part="MAX232" Quantity="1 (DNF)" Rating="" References="U1" Value="MAX232" Vendor=""/>
    </KiCAD_BOM>

