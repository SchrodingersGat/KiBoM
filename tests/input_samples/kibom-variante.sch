EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title "KiBom Test Schematic"
Date "2020-03-12"
Rev "A"
Comp "https://github.com/SchrodingersGat/KiBom"
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Device:R R1
U 1 1 5E6A2873
P 2200 2550
F 0 "R1" V 2280 2550 50  0000 C CNN
F 1 "10K" V 2200 2550 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 2130 2550 50  0001 C CNN
F 3 "~" H 2200 2550 50  0001 C CNN
	1    2200 2550
	1    0    0    -1  
$EndComp
$Comp
L Device:R R2
U 1 1 5E6A330D
P 2500 2550
F 0 "R2" V 2580 2550 50  0000 C CNN
F 1 "10K" V 2500 2550 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 2430 2550 50  0001 C CNN
F 3 "~" H 2500 2550 50  0001 C CNN
F 4 "-V2,-V3,DNC" V 2500 2550 50  0001 C CNN "Config"
	1    2500 2550
	1    0    0    -1  
$EndComp
$Comp
L Device:R R3
U 1 1 5E6A35E1
P 2750 2550
F 0 "R3" V 2830 2550 50  0000 C CNN
F 1 "10K" V 2750 2550 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 2680 2550 50  0001 C CNN
F 3 "~" H 2750 2550 50  0001 C CNN
F 4 "-V1,-V3" V 2750 2550 50  0001 C CNN "Config"
	1    2750 2550
	1    0    0    -1  
$EndComp
$Comp
L Device:R R4
U 1 1 5E6A37B2
P 3000 2550
F 0 "R4" V 3080 2550 50  0000 C CNN
F 1 "10K" V 3000 2550 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 2930 2550 50  0001 C CNN
F 3 "~" H 3000 2550 50  0001 C CNN
F 4 "+V3" V 3000 2550 50  0001 C CNN "Config"
	1    3000 2550
	1    0    0    -1  
$EndComp
Text Notes 3500 2550 0    50   ~ 0
20 x 10K resistors in 0805 package
Text Notes 550  950  0    50   ~ 0
This schematic serves as a test-file for the KiBom export script.\n\nAfter making a change to the schematic, remember to re-export the BOM to generate the intermediate .xml file\n\n(The testing framework cannot perform the netlist-export step!)
Text Notes 5950 2600 0    118  ~ 0
The test tests the following \nvariants matrix:\n      V1  V2  V3 Default\nR1    X   X   X    X\nR2    X             X\nR3        X         X\nR4             X\n\nAll other components aren't \nfitted.
$Comp
L Device:R R5
U 1 1 5F0F7340
P 2200 3000
F 0 "R5" V 2280 3000 50  0000 C CNN
F 1 "10K" V 2200 3000 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 2130 3000 50  0001 C CNN
F 3 "~" H 2200 3000 50  0001 C CNN
F 4 "DNF" V 2200 3000 50  0001 C CNN "Config"
	1    2200 3000
	1    0    0    -1  
$EndComp
$Comp
L Device:R R6
U 1 1 5F0F734B
P 2500 3000
F 0 "R6" V 2580 3000 50  0000 C CNN
F 1 "10K" V 2500 3000 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 2430 3000 50  0001 C CNN
F 3 "~" H 2500 3000 50  0001 C CNN
F 4 "DNL" V 2500 3000 50  0001 C CNN "Config"
	1    2500 3000
	1    0    0    -1  
$EndComp
$Comp
L Device:R R7
U 1 1 5F0F7356
P 2750 3000
F 0 "R7" V 2830 3000 50  0000 C CNN
F 1 "10K" V 2750 3000 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 2680 3000 50  0001 C CNN
F 3 "~" H 2750 3000 50  0001 C CNN
F 4 "DNP" V 2750 3000 50  0001 C CNN "Config"
	1    2750 3000
	1    0    0    -1  
$EndComp
$Comp
L Device:R R8
U 1 1 5F0F7361
P 3000 3000
F 0 "R8" V 3080 3000 50  0000 C CNN
F 1 "10K" V 3000 3000 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 2930 3000 50  0001 C CNN
F 3 "~" H 3000 3000 50  0001 C CNN
F 4 "Do not fit" V 3000 3000 50  0001 C CNN "Config"
	1    3000 3000
	1    0    0    -1  
$EndComp
$Comp
L Device:R R9
U 1 1 5F0F7FE1
P 2200 3450
F 0 "R9" V 2280 3450 50  0000 C CNN
F 1 "10K" V 2200 3450 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 2130 3450 50  0001 C CNN
F 3 "~" H 2200 3450 50  0001 C CNN
F 4 "Do not place" V 2200 3450 50  0001 C CNN "Config"
	1    2200 3450
	1    0    0    -1  
$EndComp
$Comp
L Device:R R10
U 1 1 5F0F7FEC
P 2500 3450
F 0 "R10" V 2580 3450 50  0000 C CNN
F 1 "10K" V 2500 3450 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 2430 3450 50  0001 C CNN
F 3 "~" H 2500 3450 50  0001 C CNN
F 4 "Do not load" V 2500 3450 50  0001 C CNN "Config"
	1    2500 3450
	1    0    0    -1  
$EndComp
$Comp
L Device:R R11
U 1 1 5F0F7FF7
P 2750 3450
F 0 "R11" V 2830 3450 50  0000 C CNN
F 1 "10K" V 2750 3450 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 2680 3450 50  0001 C CNN
F 3 "~" H 2750 3450 50  0001 C CNN
F 4 "nofit" V 2750 3450 50  0001 C CNN "Config"
	1    2750 3450
	1    0    0    -1  
$EndComp
$Comp
L Device:R R12
U 1 1 5F0F8002
P 3000 3450
F 0 "R12" V 3080 3450 50  0000 C CNN
F 1 "10K" V 3000 3450 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 2930 3450 50  0001 C CNN
F 3 "~" H 3000 3450 50  0001 C CNN
F 4 "nostuff" V 3000 3450 50  0001 C CNN "Config"
	1    3000 3450
	1    0    0    -1  
$EndComp
$Comp
L Device:R R13
U 1 1 5F0FA280
P 2200 3900
F 0 "R13" V 2280 3900 50  0000 C CNN
F 1 "10K" V 2200 3900 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 2130 3900 50  0001 C CNN
F 3 "~" H 2200 3900 50  0001 C CNN
F 4 "noplace" V 2200 3900 50  0001 C CNN "Config"
	1    2200 3900
	1    0    0    -1  
$EndComp
$Comp
L Device:R R14
U 1 1 5F0FA28B
P 2500 3900
F 0 "R14" V 2580 3900 50  0000 C CNN
F 1 "10K" V 2500 3900 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 2430 3900 50  0001 C CNN
F 3 "~" H 2500 3900 50  0001 C CNN
F 4 "noload" V 2500 3900 50  0001 C CNN "Config"
	1    2500 3900
	1    0    0    -1  
$EndComp
$Comp
L Device:R R15
U 1 1 5F0FA296
P 2750 3900
F 0 "R15" V 2830 3900 50  0000 C CNN
F 1 "10K" V 2750 3900 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 2680 3900 50  0001 C CNN
F 3 "~" H 2750 3900 50  0001 C CNN
F 4 "not fitted" V 2750 3900 50  0001 C CNN "Config"
	1    2750 3900
	1    0    0    -1  
$EndComp
$Comp
L Device:R R16
U 1 1 5F0FA2A1
P 3000 3900
F 0 "R16" V 3080 3900 50  0000 C CNN
F 1 "10K" V 3000 3900 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 2930 3900 50  0001 C CNN
F 3 "~" H 3000 3900 50  0001 C CNN
F 4 "not loaded" V 3000 3900 50  0001 C CNN "Config"
	1    3000 3900
	1    0    0    -1  
$EndComp
$Comp
L Device:R R17
U 1 1 5F0FCAA9
P 2200 4350
F 0 "R17" V 2280 4350 50  0000 C CNN
F 1 "10K" V 2200 4350 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 2130 4350 50  0001 C CNN
F 3 "~" H 2200 4350 50  0001 C CNN
F 4 "not placed" V 2200 4350 50  0001 C CNN "Config"
	1    2200 4350
	1    0    0    -1  
$EndComp
$Comp
L Device:R R18
U 1 1 5F0FCAB4
P 2500 4350
F 0 "R18" V 2580 4350 50  0000 C CNN
F 1 "10K" V 2500 4350 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 2430 4350 50  0001 C CNN
F 3 "~" H 2500 4350 50  0001 C CNN
F 4 "no stuff" V 2500 4350 50  0001 C CNN "Config"
	1    2500 4350
	1    0    0    -1  
$EndComp
$Comp
L Device:R R19
U 1 1 5F0FCABF
P 2750 4350
F 0 "R19" V 2830 4350 50  0000 C CNN
F 1 "10K" V 2750 4350 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 2680 4350 50  0001 C CNN
F 3 "~" H 2750 4350 50  0001 C CNN
F 4 "bla bla DNF ble DNC ble " V 2750 4350 50  0001 C CNN "Config"
	1    2750 4350
	1    0    0    -1  
$EndComp
$Comp
L Device:R R20
U 1 1 5F0FCACA
P 3000 4350
F 0 "R20" V 3080 4350 50  0000 C CNN
F 1 "10K" V 3000 4350 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 2930 4350 50  0001 C CNN
F 3 "~" H 3000 4350 50  0001 C CNN
F 4 "bla,bla,DNF,ble" V 3000 4350 50  0001 C CNN "Config"
	1    3000 4350
	1    0    0    -1  
$EndComp
$EndSCHEMATC
