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
	1    3000 2550
	1    0    0    -1  
$EndComp
$Comp
L Device:R R5
U 1 1 5E6A39EB
P 3250 2550
F 0 "R5" V 3330 2550 50  0000 C CNN
F 1 "10K" V 3250 2550 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 3180 2550 50  0001 C CNN
F 3 "~" H 3250 2550 50  0001 C CNN
	1    3250 2550
	1    0    0    -1  
$EndComp
Text Notes 3500 2550 0    50   ~ 0
5 x 10K resistors in 0805 package
$Comp
L Device:R R6
U 1 1 5E6A3CA0
P 2200 3100
F 0 "R6" V 2280 3100 50  0000 C CNN
F 1 "4K7" V 2200 3100 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 2130 3100 50  0001 C CNN
F 3 "~" H 2200 3100 50  0001 C CNN
	1    2200 3100
	1    0    0    -1  
$EndComp
$Comp
L Device:R R7
U 1 1 5E6A3F38
P 2500 3100
F 0 "R7" V 2580 3100 50  0000 C CNN
F 1 "4700" V 2500 3100 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 2430 3100 50  0001 C CNN
F 3 "~" H 2500 3100 50  0001 C CNN
	1    2500 3100
	1    0    0    -1  
$EndComp
$Comp
L Device:R R8
U 1 1 5E6A4181
P 2750 3100
F 0 "R8" V 2830 3100 50  0000 C CNN
F 1 "4.7K" V 2750 3100 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 2680 3100 50  0001 C CNN
F 3 "~" H 2750 3100 50  0001 C CNN
	1    2750 3100
	1    0    0    -1  
$EndComp
Text Notes 3500 3150 0    50   ~ 0
3 x 4K7 resistors in 0805 package\nNote: Values are identical even if specified differently
$Comp
L Device:R R9
U 1 1 5E6A448B
P 2200 3650
F 0 "R9" V 2280 3650 50  0000 C CNN
F 1 "4K7" V 2200 3650 50  0000 C CNN
F 2 "Resistor_SMD:R_0603_1608Metric" V 2130 3650 50  0001 C CNN
F 3 "~" H 2200 3650 50  0001 C CNN
	1    2200 3650
	1    0    0    -1  
$EndComp
$Comp
L Device:R R10
U 1 1 5E6A491A
P 2500 3650
F 0 "R10" V 2580 3650 50  0000 C CNN
F 1 "4K7" V 2500 3650 50  0000 C CNN
F 2 "Resistor_SMD:R_0603_1608Metric" V 2430 3650 50  0001 C CNN
F 3 "~" H 2500 3650 50  0001 C CNN
	1    2500 3650
	1    0    0    -1  
$EndComp
Text Notes 3500 3650 0    50   ~ 0
3 x 4K7 resistors in 0603 package
Text Notes 550  950  0    50   ~ 0
This schematic serves as a test-file for the KiBom export script.\n\nAfter making a change to the schematic, remember to re-export the BOM to generate the intermediate .xml file\n\n(The testing framework cannot perform the netlist-export step!)
$Comp
L Device:C C1
U 1 1 5E6A62CC
P 6650 2550
F 0 "C1" H 6675 2650 50  0000 L CNN
F 1 "10nF" H 6675 2450 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 6688 2400 50  0001 C CNN
F 3 "~" H 6650 2550 50  0001 C CNN
	1    6650 2550
	1    0    0    -1  
$EndComp
$Comp
L Device:C C2
U 1 1 5E6A6854
P 7050 2550
F 0 "C2" H 7075 2650 50  0000 L CNN
F 1 "10n" H 7075 2450 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 7088 2400 50  0001 C CNN
F 3 "~" H 7050 2550 50  0001 C CNN
	1    7050 2550
	1    0    0    -1  
$EndComp
$Comp
L Device:C C3
U 1 1 5E6A6A34
P 7450 2550
F 0 "C3" H 7475 2650 50  0000 L CNN
F 1 "0.01uF" H 7475 2450 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 7488 2400 50  0001 C CNN
F 3 "~" H 7450 2550 50  0001 C CNN
	1    7450 2550
	1    0    0    -1  
$EndComp
$Comp
L Device:C C4
U 1 1 5E6A6CB6
P 7900 2550
F 0 "C4" H 7925 2650 50  0000 L CNN
F 1 "0.01uf" H 7925 2450 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 7938 2400 50  0001 C CNN
F 3 "~" H 7900 2550 50  0001 C CNN
	1    7900 2550
	1    0    0    -1  
$EndComp
$EndSCHEMATC
