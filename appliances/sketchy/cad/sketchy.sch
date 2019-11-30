EESchema Schematic File Version 5
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
Comment5 ""
Comment6 ""
Comment7 ""
Comment8 ""
Comment9 ""
$EndDescr
$Comp
L Connector:Barrel_Jack J1
U 1 1 5DDC16F9
P 1700 1300
F 0 "J1" H 1757 1625 50  0000 C CNN
F 1 "Barrel_Jack" H 1757 1534 50  0000 C CNN
F 2 "Connectors:Barrel_Jack_CUI_PJ-102AH" H 1750 1260 50  0001 C CNN
F 3 "~" H 1750 1260 50  0001 C CNN
	1    1700 1300
	1    0    0    -1  
$EndComp
Text GLabel 2250 1200 2    50   Input ~ 0
VDD
Text GLabel 2250 1400 2    50   Input ~ 0
GND
Wire Wire Line
	2250 1200 2000 1200
Wire Wire Line
	2250 1400 2000 1400
$Comp
L custom:ESP32PICO-KIT U1
U 1 1 5DDBE11A
P 2200 1750
F 0 "U1" H 1858 1748 50  0000 C CNN
F 1 "ESP32PICO-KIT" H 1858 1657 50  0000 C CNN
F 2 "Modules-custom:ESP32-PICO-KIT" H 2200 1400 50  0001 C CNN
F 3 "" H 2200 1400 50  0001 C CNN
	1    2200 1750
	1    0    0    -1  
$EndComp
Text GLabel 2500 5900 2    50   Input ~ 0
NOT_ENABLE
Text GLabel 2500 6100 2    50   Input ~ 0
GND
Text GLabel 2500 6200 2    50   Input ~ 0
VDD
Wire Wire Line
	2200 6200 2500 6200
Wire Wire Line
	2500 6100 2200 6100
Text GLabel 2500 5800 2    50   Input ~ 0
STEPPER_X_STEP
Text GLabel 2500 5700 2    50   Input ~ 0
STEPPER_X_DIR
Wire Wire Line
	2500 5700 2200 5700
Text GLabel 2500 5500 2    50   Input ~ 0
STEPPER_Y_DIR
Text GLabel 2500 5600 2    50   Input ~ 0
STEPPER_Y_STEP
Text GLabel 2350 4250 2    50   Input ~ 0
3V3
Text GLabel 2500 6000 2    50   Input ~ 0
3V3
Wire Wire Line
	2500 6000 2200 6000
Wire Wire Line
	4300 5000 4450 5000
Text GLabel 4250 5200 0    50   Input ~ 0
NOT_ENABLE
Wire Wire Line
	4250 5200 4450 5200
Text GLabel 4250 5300 0    50   Input ~ 0
STEPPER_Y_STEP
Wire Wire Line
	4250 5300 4450 5300
Text GLabel 4250 5400 0    50   Input ~ 0
STEPPER_Y_DIR
Wire Wire Line
	4250 5400 4450 5400
Wire Wire Line
	4450 5700 4300 5700
Wire Wire Line
	4450 5600 4300 5600
Wire Wire Line
	4300 5600 4300 5700
Connection ~ 4300 5700
$Comp
L Motor:Stepper_Motor_bipolar M2
U 1 1 5DDEB845
P 6150 5400
F 0 "M2" H 6338 5524 50  0000 L CNN
F 1 "Stepper_Motor_bipolar" H 6338 5433 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Angled_1x04_Pitch2.54mm" H 6160 5390 50  0001 C CNN
F 3 "http://www.infineon.com/dgdl/Application-Note-TLE8110EE_driving_UniPolarStepperMotor_V1.1.pdf?fileId=db3a30431be39b97011be5d0aa0a00b0" H 6160 5390 50  0001 C CNN
	1    6150 5400
	0    -1   1    0   
$EndComp
$Comp
L Driver_Motor:Pololu_Breakout_A4988 A2
U 1 1 5DDE9836
P 4850 5300
F 0 "A2" H 5600 6181 50  0000 C CNN
F 1 "Pololu_Breakout_A4988" H 5600 6090 50  0000 C CNN
F 2 "Modules:Pololu_Breakout-16_15.2x20.3mm" H 5125 4550 50  0001 L CNN
F 3 "https://www.pololu.com/product/2980/pictures" H 4950 5000 50  0001 C CNN
	1    4850 5300
	1    0    0    -1  
$EndComp
Wire Wire Line
	5050 6100 5050 6250
Connection ~ 4300 5800
Connection ~ 5050 6250
Wire Wire Line
	5050 6250 5050 6400
Wire Wire Line
	4300 5700 4300 5800
Wire Wire Line
	4450 5800 4300 5800
Text GLabel 5050 6400 3    50   Input ~ 0
GND
Wire Wire Line
	4300 5800 4300 6250
Wire Wire Line
	4300 6250 4850 6250
Wire Wire Line
	4850 6100 4850 6250
Connection ~ 4850 6250
Wire Wire Line
	4850 6250 5050 6250
Text GLabel 5050 4450 1    50   Input ~ 0
VDD
Wire Wire Line
	5050 4450 5050 4600
Wire Wire Line
	4300 4900 4300 5000
Text GLabel 4850 4450 1    50   Input ~ 0
3V3
Wire Wire Line
	4450 4900 4300 4900
Wire Wire Line
	4850 4450 4850 4550
Wire Wire Line
	4300 4900 4300 4550
Wire Wire Line
	4300 4550 4850 4550
Connection ~ 4300 4900
Connection ~ 4850 4550
Wire Wire Line
	4850 4550 4850 4600
Wire Wire Line
	5700 5300 5850 5300
Wire Wire Line
	5350 5300 5600 5300
Wire Wire Line
	5600 5300 5600 4950
Wire Wire Line
	5600 4950 6050 4950
Wire Wire Line
	6050 4950 6050 5100
Wire Wire Line
	5350 5200 5350 4900
Wire Wire Line
	5350 4900 6250 4900
Wire Wire Line
	6250 4900 6250 5100
Wire Wire Line
	4850 3750 5050 3750
Wire Wire Line
	4250 2700 4450 2700
Wire Wire Line
	5350 2800 5600 2800
Wire Wire Line
	6050 2450 6050 2600
Wire Wire Line
	5600 2800 5600 2450
Wire Wire Line
	6250 2400 6250 2600
Wire Wire Line
	5350 2700 5350 2400
Wire Wire Line
	5600 2450 6050 2450
Connection ~ 4850 3750
Wire Wire Line
	5350 2400 6250 2400
Wire Wire Line
	4300 3100 4300 3200
Wire Wire Line
	4300 2400 4300 2050
$Comp
L Motor:Stepper_Motor_bipolar M1
U 1 1 5DDF7CA3
P 6150 2900
F 0 "M1" H 6338 3024 50  0000 L CNN
F 1 "Stepper_Motor_bipolar" H 6338 2933 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Angled_1x04_Pitch2.54mm" H 6160 2890 50  0001 C CNN
F 3 "http://www.infineon.com/dgdl/Application-Note-TLE8110EE_driving_UniPolarStepperMotor_V1.1.pdf?fileId=db3a30431be39b97011be5d0aa0a00b0" H 6160 2890 50  0001 C CNN
	1    6150 2900
	0    -1   1    0   
$EndComp
Connection ~ 4300 2400
Connection ~ 4850 2050
Wire Wire Line
	5050 1950 5050 2100
Wire Wire Line
	4850 2050 4850 2100
Wire Wire Line
	4300 2050 4850 2050
Wire Wire Line
	5700 2800 5850 2800
Wire Wire Line
	4850 3600 4850 3750
Wire Wire Line
	4300 3750 4850 3750
Text GLabel 4250 2900 0    50   Input ~ 0
STEPPER_X_DIR
Wire Wire Line
	4450 3100 4300 3100
Text GLabel 4250 2700 0    50   Input ~ 0
NOT_ENABLE
Wire Wire Line
	4300 3300 4300 3750
Text GLabel 5050 3900 3    50   Input ~ 0
GND
Wire Wire Line
	4450 3300 4300 3300
Wire Wire Line
	4300 2500 4450 2500
Wire Wire Line
	4450 2400 4300 2400
Wire Wire Line
	4300 3200 4300 3300
Wire Wire Line
	4450 3200 4300 3200
Text GLabel 4850 1950 1    50   Input ~ 0
3V3
Wire Wire Line
	5050 3750 5050 3900
Text GLabel 4250 2800 0    50   Input ~ 0
STEPPER_X_STEP
Text GLabel 5050 1950 1    50   Input ~ 0
VDD
Wire Wire Line
	4850 1950 4850 2050
Connection ~ 5050 3750
Connection ~ 4300 3300
Connection ~ 4300 3200
Wire Wire Line
	4250 2900 4450 2900
Wire Wire Line
	5050 3600 5050 3750
$Comp
L Driver_Motor:Pololu_Breakout_A4988 A1
U 1 1 5DDF7CD9
P 4850 2800
F 0 "A1" H 5600 3681 50  0000 C CNN
F 1 "Pololu_Breakout_A4988" H 5600 3590 50  0000 C CNN
F 2 "Modules:Pololu_Breakout-16_15.2x20.3mm" H 5125 2050 50  0001 L CNN
F 3 "https://www.pololu.com/product/2980/pictures" H 4950 2500 50  0001 C CNN
	1    4850 2800
	1    0    0    -1  
$EndComp
Wire Wire Line
	4250 2800 4450 2800
Wire Wire Line
	4300 2400 4300 2500
Wire Wire Line
	5700 5500 5350 5500
Wire Wire Line
	5700 5300 5700 5500
Wire Wire Line
	5850 5500 5850 5400
Wire Wire Line
	5850 5400 5350 5400
Wire Wire Line
	5700 3000 5350 3000
Wire Wire Line
	5700 2800 5700 3000
Wire Wire Line
	5350 2900 5850 2900
Wire Wire Line
	5850 2900 5850 3000
Wire Wire Line
	2500 5900 2200 5900
Wire Wire Line
	2500 5500 2200 5500
Wire Wire Line
	2500 5600 2200 5600
Wire Wire Line
	2500 5800 2200 5800
$Comp
L Connector_Generic:Conn_01x09 J4
U 1 1 5DDFE4C5
P 2550 5000
F 0 "J4" V 2767 4996 50  0000 C CNN
F 1 "Conn_01x09" V 2676 4996 50  0000 C CNN
F 2 "Pin_Header_Straight_1x09_Pitch2.54mm" H 2550 5000 50  0001 C CNN
F 3 "~" H 2550 5000 50  0001 C CNN
	1    2550 5000
	1    0    0    1   
$EndComp
Wire Wire Line
	2200 5400 2350 5400
Wire Wire Line
	2350 5300 2200 5300
Wire Wire Line
	2200 5200 2350 5200
Wire Wire Line
	2350 5100 2200 5100
Wire Wire Line
	2200 5000 2350 5000
Wire Wire Line
	2350 4900 2200 4900
Wire Wire Line
	2200 4800 2350 4800
Wire Wire Line
	2350 4700 2200 4700
Wire Wire Line
	2200 4600 2350 4600
$Comp
L Connector_Generic:Conn_01x17 J2
U 1 1 5DDFE417
P 2550 3200
F 0 "J2" H 2468 2175 50  0000 C CNN
F 1 "Conn_01x17" H 2468 2266 50  0000 C CNN
F 2 "" H 2550 3200 50  0001 C CNN
F 3 "~" H 2550 3200 50  0001 C CNN
	1    2550 3200
	1    0    0    1   
$EndComp
Wire Wire Line
	2350 3900 2300 3900
Wire Wire Line
	2350 3800 2200 3800
Wire Wire Line
	2350 3700 2200 3700
Wire Wire Line
	2200 3600 2350 3600
Wire Wire Line
	2350 3500 2200 3500
Wire Wire Line
	2200 3400 2350 3400
Wire Wire Line
	2350 3300 2200 3300
Wire Wire Line
	2200 3200 2350 3200
Wire Wire Line
	2350 3100 2200 3100
Wire Wire Line
	2200 3000 2350 3000
Wire Wire Line
	2350 2900 2200 2900
Wire Wire Line
	2200 2800 2350 2800
Wire Wire Line
	2350 2700 2200 2700
Wire Wire Line
	2200 2600 2350 2600
Wire Wire Line
	2350 2500 2200 2500
Wire Wire Line
	2200 2400 2350 2400
Text GLabel 2350 4150 2    50   Input ~ 0
GND
Wire Wire Line
	2350 4150 2300 4150
Connection ~ 2300 3900
Wire Wire Line
	2300 3900 2200 3900
Wire Wire Line
	2200 4000 2250 4000
Wire Wire Line
	2250 4250 2250 4000
Wire Wire Line
	2250 4250 2350 4250
Connection ~ 2250 4000
Wire Wire Line
	2300 3900 2300 4150
Wire Wire Line
	2250 4000 2350 4000
$EndSCHEMATC
