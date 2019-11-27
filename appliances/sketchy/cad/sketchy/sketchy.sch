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
P 3200 1950
F 0 "U1" H 2858 1948 50  0000 C CNN
F 1 "ESP32PICO-KIT" H 2858 1857 50  0000 C CNN
F 2 "Modules-custom:ESP32-PICO-KIT" H 3200 1600 50  0001 C CNN
F 3 "" H 3200 1600 50  0001 C CNN
	1    3200 1950
	1    0    0    -1  
$EndComp
Text GLabel 3500 6100 2    50   Input ~ 0
NOT_ENABLE
Wire Wire Line
	3500 4100 3200 4100
Text GLabel 3500 4100 2    50   Input ~ 0
GND
Text GLabel 3500 6300 2    50   Input ~ 0
GND
Text GLabel 3500 6400 2    50   Input ~ 0
VDD
Wire Wire Line
	3200 6400 3500 6400
Wire Wire Line
	3500 6300 3200 6300
Text GLabel 3500 6000 2    50   Input ~ 0
STEPPER_X_STEP
Text GLabel 3500 5900 2    50   Input ~ 0
STEPPER_X_DIR
Wire Wire Line
	3500 5900 3200 5900
Text GLabel 3500 5700 2    50   Input ~ 0
STEPPER_Y_DIR
Text GLabel 3500 5800 2    50   Input ~ 0
STEPPER_Y_STEP
Text GLabel 3500 4200 2    50   Input ~ 0
3V3
Wire Wire Line
	3500 4200 3200 4200
Text GLabel 3500 6200 2    50   Input ~ 0
3V3
Wire Wire Line
	3500 6200 3200 6200
NoConn ~ 3350 2300
Wire Wire Line
	3350 2300 3200 2300
Wire Wire Line
	3350 2400 3200 2400
NoConn ~ 3350 2400
Wire Wire Line
	3350 2500 3200 2500
NoConn ~ 3350 2500
Wire Wire Line
	3350 2600 3200 2600
NoConn ~ 3350 2600
Wire Wire Line
	3350 2700 3200 2700
NoConn ~ 3350 2700
Wire Wire Line
	3350 2800 3200 2800
NoConn ~ 3350 2800
Wire Wire Line
	3350 2900 3200 2900
NoConn ~ 3350 2900
Wire Wire Line
	3350 3000 3200 3000
NoConn ~ 3350 3000
Wire Wire Line
	3350 3100 3200 3100
NoConn ~ 3350 3100
Wire Wire Line
	3350 3200 3200 3200
NoConn ~ 3350 3200
Wire Wire Line
	3350 3300 3200 3300
NoConn ~ 3350 3300
Wire Wire Line
	3350 3400 3200 3400
NoConn ~ 3350 3400
Wire Wire Line
	3350 3500 3200 3500
NoConn ~ 3350 3500
Wire Wire Line
	3350 3600 3200 3600
NoConn ~ 3350 3600
Wire Wire Line
	3350 3700 3200 3700
NoConn ~ 3350 3700
Wire Wire Line
	3350 3800 3200 3800
NoConn ~ 3350 3800
Wire Wire Line
	3350 3900 3200 3900
NoConn ~ 3350 3900
Wire Wire Line
	3350 4000 3200 4000
NoConn ~ 3350 4000
Wire Wire Line
	3350 4500 3200 4500
NoConn ~ 3350 4500
Wire Wire Line
	3350 4600 3200 4600
NoConn ~ 3350 4600
Wire Wire Line
	3350 4700 3200 4700
NoConn ~ 3350 4700
Wire Wire Line
	3350 4800 3200 4800
NoConn ~ 3350 4800
Wire Wire Line
	3350 4900 3200 4900
NoConn ~ 3350 4900
Wire Wire Line
	3350 5000 3200 5000
NoConn ~ 3350 5000
Wire Wire Line
	3350 5100 3200 5100
NoConn ~ 3350 5100
Wire Wire Line
	3350 5200 3200 5200
NoConn ~ 3350 5200
Wire Wire Line
	3350 5300 3200 5300
NoConn ~ 3350 5300
Wire Wire Line
	3350 5400 3200 5400
NoConn ~ 3350 5400
Wire Wire Line
	3350 5500 3200 5500
NoConn ~ 3350 5500
Wire Wire Line
	3350 5600 3200 5600
NoConn ~ 3350 5600
Wire Wire Line
	7100 4550 7250 4550
Text GLabel 7050 4750 0    50   Input ~ 0
NOT_ENABLE
Wire Wire Line
	7050 4750 7250 4750
Text GLabel 7050 4850 0    50   Input ~ 0
STEPPER_Y_STEP
Wire Wire Line
	7050 4850 7250 4850
Text GLabel 7050 4950 0    50   Input ~ 0
STEPPER_Y_DIR
Wire Wire Line
	7050 4950 7250 4950
Wire Wire Line
	7250 5250 7100 5250
Wire Wire Line
	7250 5150 7100 5150
Wire Wire Line
	7100 5150 7100 5250
Connection ~ 7100 5250
$Comp
L Motor:Stepper_Motor_bipolar M2
U 1 1 5DDEB845
P 8950 4950
F 0 "M2" H 9138 5074 50  0000 L CNN
F 1 "Stepper_Motor_bipolar" H 9138 4983 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Angled_1x04_Pitch2.54mm" H 8960 4940 50  0001 C CNN
F 3 "http://www.infineon.com/dgdl/Application-Note-TLE8110EE_driving_UniPolarStepperMotor_V1.1.pdf?fileId=db3a30431be39b97011be5d0aa0a00b0" H 8960 4940 50  0001 C CNN
	1    8950 4950
	0    -1   1    0   
$EndComp
$Comp
L Driver_Motor:Pololu_Breakout_A4988 A2
U 1 1 5DDE9836
P 7650 4850
F 0 "A2" H 8400 5731 50  0000 C CNN
F 1 "Pololu_Breakout_A4988" H 8400 5640 50  0000 C CNN
F 2 "Modules:Pololu_Breakout-16_15.2x20.3mm" H 7925 4100 50  0001 L CNN
F 3 "https://www.pololu.com/product/2980/pictures" H 7750 4550 50  0001 C CNN
	1    7650 4850
	1    0    0    -1  
$EndComp
Wire Wire Line
	7850 5650 7850 5800
Connection ~ 7100 5350
Connection ~ 7850 5800
Wire Wire Line
	7850 5800 7850 5950
Wire Wire Line
	7100 5250 7100 5350
Wire Wire Line
	7250 5350 7100 5350
Text GLabel 7850 5950 3    50   Input ~ 0
GND
Wire Wire Line
	7100 5350 7100 5800
Wire Wire Line
	7100 5800 7650 5800
Wire Wire Line
	7650 5650 7650 5800
Connection ~ 7650 5800
Wire Wire Line
	7650 5800 7850 5800
Text GLabel 7850 4000 1    50   Input ~ 0
VDD
Wire Wire Line
	7850 4000 7850 4150
Wire Wire Line
	7100 4450 7100 4550
Text GLabel 7650 4000 1    50   Input ~ 0
3V3
Wire Wire Line
	7250 4450 7100 4450
Wire Wire Line
	7650 4000 7650 4100
Wire Wire Line
	7100 4450 7100 4100
Wire Wire Line
	7100 4100 7650 4100
Connection ~ 7100 4450
Connection ~ 7650 4100
Wire Wire Line
	7650 4100 7650 4150
Wire Wire Line
	8500 4850 8650 4850
Wire Wire Line
	8150 4850 8400 4850
Wire Wire Line
	8400 4850 8400 4500
Wire Wire Line
	8400 4500 8850 4500
Wire Wire Line
	8850 4500 8850 4650
Wire Wire Line
	8150 4750 8150 4450
Wire Wire Line
	8150 4450 9050 4450
Wire Wire Line
	9050 4450 9050 4650
Wire Wire Line
	7650 3300 7850 3300
Wire Wire Line
	7050 2250 7250 2250
Wire Wire Line
	8150 2350 8400 2350
Wire Wire Line
	8850 2000 8850 2150
Wire Wire Line
	8400 2350 8400 2000
Wire Wire Line
	9050 1950 9050 2150
Wire Wire Line
	8150 2250 8150 1950
Wire Wire Line
	8400 2000 8850 2000
Connection ~ 7650 3300
Wire Wire Line
	8150 1950 9050 1950
Wire Wire Line
	7100 2650 7100 2750
Wire Wire Line
	7100 1950 7100 1600
$Comp
L Motor:Stepper_Motor_bipolar M1
U 1 1 5DDF7CA3
P 8950 2450
F 0 "M1" H 9138 2574 50  0000 L CNN
F 1 "Stepper_Motor_bipolar" H 9138 2483 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Angled_1x04_Pitch2.54mm" H 8960 2440 50  0001 C CNN
F 3 "http://www.infineon.com/dgdl/Application-Note-TLE8110EE_driving_UniPolarStepperMotor_V1.1.pdf?fileId=db3a30431be39b97011be5d0aa0a00b0" H 8960 2440 50  0001 C CNN
	1    8950 2450
	0    -1   1    0   
$EndComp
Connection ~ 7100 1950
Connection ~ 7650 1600
Wire Wire Line
	7850 1500 7850 1650
Wire Wire Line
	7650 1600 7650 1650
Wire Wire Line
	7100 1600 7650 1600
Wire Wire Line
	8500 2350 8650 2350
Wire Wire Line
	7650 3150 7650 3300
Wire Wire Line
	7100 3300 7650 3300
Text GLabel 7050 2450 0    50   Input ~ 0
STEPPER_X_DIR
Wire Wire Line
	7250 2650 7100 2650
Text GLabel 7050 2250 0    50   Input ~ 0
NOT_ENABLE
Wire Wire Line
	7100 2850 7100 3300
Text GLabel 7850 3450 3    50   Input ~ 0
GND
Wire Wire Line
	7250 2850 7100 2850
Wire Wire Line
	7100 2050 7250 2050
Wire Wire Line
	7250 1950 7100 1950
Wire Wire Line
	7100 2750 7100 2850
Wire Wire Line
	7250 2750 7100 2750
Text GLabel 7650 1500 1    50   Input ~ 0
3V3
Wire Wire Line
	7850 3300 7850 3450
Text GLabel 7050 2350 0    50   Input ~ 0
STEPPER_X_STEP
Text GLabel 7850 1500 1    50   Input ~ 0
VDD
Wire Wire Line
	7650 1500 7650 1600
Connection ~ 7850 3300
Connection ~ 7100 2850
Connection ~ 7100 2750
Wire Wire Line
	7050 2450 7250 2450
Wire Wire Line
	7850 3150 7850 3300
$Comp
L Driver_Motor:Pololu_Breakout_A4988 A1
U 1 1 5DDF7CD9
P 7650 2350
F 0 "A1" H 8400 3231 50  0000 C CNN
F 1 "Pololu_Breakout_A4988" H 8400 3140 50  0000 C CNN
F 2 "Modules:Pololu_Breakout-16_15.2x20.3mm" H 7925 1600 50  0001 L CNN
F 3 "https://www.pololu.com/product/2980/pictures" H 7750 2050 50  0001 C CNN
	1    7650 2350
	1    0    0    -1  
$EndComp
Wire Wire Line
	7050 2350 7250 2350
Wire Wire Line
	7100 1950 7100 2050
Wire Wire Line
	8500 5050 8150 5050
Wire Wire Line
	8500 4850 8500 5050
Wire Wire Line
	8650 5050 8650 4950
Wire Wire Line
	8650 4950 8150 4950
Wire Wire Line
	8500 2550 8150 2550
Wire Wire Line
	8500 2350 8500 2550
Wire Wire Line
	8150 2450 8650 2450
Wire Wire Line
	8650 2450 8650 2550
Wire Wire Line
	3500 6100 3200 6100
Wire Wire Line
	3500 5700 3200 5700
Wire Wire Line
	3500 5800 3200 5800
Wire Wire Line
	3500 6000 3200 6000
$EndSCHEMATC
