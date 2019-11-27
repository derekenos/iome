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
L Driver_Motor:Pololu_Breakout_DRV8825 A1
U 1 1 5DDBD2EF
P 7650 2400
F 0 "A1" H 8300 3181 50  0000 C CNN
F 1 "Pololu_Breakout_DRV8825" H 8300 3090 50  0000 C CNN
F 2 "Modules:Pololu_Breakout-16_15.2x20.3mm" H 7850 1600 50  0001 L CNN
F 3 "https://www.pololu.com/product/2982" H 7750 2100 50  0001 C CNN
	1    7650 2400
	1    0    0    -1  
$EndComp
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
Text GLabel 7650 1650 1    50   Input ~ 0
VDD
Wire Wire Line
	7000 2200 7250 2200
Wire Wire Line
	7250 2100 7000 2100
Connection ~ 7000 2100
Wire Wire Line
	7000 2100 7000 2200
Wire Wire Line
	7250 2000 7000 2000
Wire Wire Line
	7000 2000 7000 2100
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
Text GLabel 7750 3500 3    50   Input ~ 0
GND
Text GLabel 7050 2400 0    50   Input ~ 0
NOT_ENABLE
Wire Wire Line
	7050 2400 7250 2400
Text GLabel 3500 5700 2    50   Input ~ 0
NOT_ENABLE
Wire Wire Line
	3500 5700 3200 5700
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
Text GLabel 7050 2500 0    50   Input ~ 0
STEPPER_X_STEP
Wire Wire Line
	7050 2500 7250 2500
Text GLabel 3500 5800 2    50   Input ~ 0
STEPPER_X_STEP
Wire Wire Line
	3500 5800 3200 5800
Text GLabel 3500 5900 2    50   Input ~ 0
STEPPER_X_DIR
Wire Wire Line
	3500 5900 3200 5900
Text GLabel 7050 2600 0    50   Input ~ 0
STEPPER_X_DIR
Wire Wire Line
	7050 2600 7250 2600
Text GLabel 3500 6100 2    50   Input ~ 0
STEPPER_Y_DIR
Text GLabel 3500 6000 2    50   Input ~ 0
STEPPER_Y_STEP
Wire Wire Line
	3500 6000 3200 6000
Wire Wire Line
	3200 6100 3500 6100
$Comp
L Motor:Stepper_Motor_bipolar M1
U 1 1 5DDCAA64
P 8850 2600
F 0 "M1" H 9038 2724 50  0000 L CNN
F 1 "Stepper_Motor_bipolar" H 9038 2633 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Angled_1x04_Pitch2.54mm" H 8860 2590 50  0001 C CNN
F 3 "http://www.infineon.com/dgdl/Application-Note-TLE8110EE_driving_UniPolarStepperMotor_V1.1.pdf?fileId=db3a30431be39b97011be5d0aa0a00b0" H 8860 2590 50  0001 C CNN
	1    8850 2600
	0    -1   1    0   
$EndComp
Wire Wire Line
	7650 3200 7650 3350
Wire Wire Line
	7650 3350 7750 3350
Wire Wire Line
	7750 3200 7750 3350
Connection ~ 7750 3350
Wire Wire Line
	7750 3350 7750 3500
Text GLabel 3500 4200 2    50   Input ~ 0
3V3
Wire Wire Line
	7650 1650 7650 1800
Wire Wire Line
	3500 4200 3200 4200
Text GLabel 3500 6200 2    50   Input ~ 0
3V3
Wire Wire Line
	3500 6200 3200 6200
Text GLabel 7000 1650 1    50   Input ~ 0
3V3
Wire Wire Line
	7000 1650 7000 2000
Connection ~ 7000 2000
Wire Wire Line
	7250 3000 7150 3000
Wire Wire Line
	7150 3000 7150 3350
Wire Wire Line
	7150 3350 7650 3350
Connection ~ 7650 3350
Wire Wire Line
	7250 2900 7150 2900
Wire Wire Line
	7150 2900 7150 3000
Connection ~ 7150 3000
Wire Wire Line
	7250 2800 7150 2800
Wire Wire Line
	7150 2800 7150 2900
Connection ~ 7150 2900
Connection ~ 7650 5750
$Comp
L Driver_Motor:Pololu_Breakout_DRV8825 A2
U 1 1 5DDDC469
P 7650 4800
F 0 "A2" H 8300 5581 50  0000 C CNN
F 1 "Pololu_Breakout_DRV8825" H 8300 5490 50  0000 C CNN
F 2 "Modules:Pololu_Breakout-16_15.2x20.3mm" H 7850 4000 50  0001 L CNN
F 3 "https://www.pololu.com/product/2982" H 7750 4500 50  0001 C CNN
	1    7650 4800
	1    0    0    -1  
$EndComp
Connection ~ 7000 4500
Text GLabel 7650 4050 1    50   Input ~ 0
VDD
Wire Wire Line
	7000 4600 7250 4600
Wire Wire Line
	7250 4500 7000 4500
Wire Wire Line
	7000 4500 7000 4600
Wire Wire Line
	7250 4400 7000 4400
Wire Wire Line
	7000 4400 7000 4500
Text GLabel 7750 5900 3    50   Input ~ 0
GND
Text GLabel 7050 4800 0    50   Input ~ 0
NOT_ENABLE
Wire Wire Line
	7050 4800 7250 4800
Text GLabel 7050 4900 0    50   Input ~ 0
STEPPER_Y_STEP
Wire Wire Line
	7050 4900 7250 4900
Text GLabel 7050 5000 0    50   Input ~ 0
STEPPER_Y_DIR
Wire Wire Line
	7050 5000 7250 5000
$Comp
L Motor:Stepper_Motor_bipolar M2
U 1 1 5DDDC4B2
P 8850 5000
F 0 "M2" H 9038 5124 50  0000 L CNN
F 1 "Stepper_Motor_bipolar" H 9038 5033 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Angled_1x04_Pitch2.54mm" H 8860 4990 50  0001 C CNN
F 3 "http://www.infineon.com/dgdl/Application-Note-TLE8110EE_driving_UniPolarStepperMotor_V1.1.pdf?fileId=db3a30431be39b97011be5d0aa0a00b0" H 8860 4990 50  0001 C CNN
	1    8850 5000
	0    -1   1    0   
$EndComp
Connection ~ 7750 5750
Wire Wire Line
	7650 5600 7650 5750
Wire Wire Line
	7650 5750 7750 5750
Wire Wire Line
	7750 5600 7750 5750
Connection ~ 7000 4400
Wire Wire Line
	7750 5750 7750 5900
Wire Wire Line
	7650 4050 7650 4200
Text GLabel 7000 4050 1    50   Input ~ 0
3V3
Wire Wire Line
	7000 4050 7000 4400
Wire Wire Line
	8050 4700 8250 4700
Wire Wire Line
	8250 4700 8250 4600
Wire Wire Line
	7150 5200 7150 5300
Connection ~ 7150 5300
Wire Wire Line
	7250 5200 7150 5200
Wire Wire Line
	7150 5300 7150 5400
Connection ~ 7150 5400
Wire Wire Line
	7150 5750 7650 5750
Wire Wire Line
	7250 5300 7150 5300
Wire Wire Line
	7250 5400 7150 5400
Wire Wire Line
	7150 5400 7150 5750
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
	8550 4900 8350 4900
Wire Wire Line
	8350 5100 8350 4900
Wire Wire Line
	8050 5000 8550 5000
Wire Wire Line
	8550 5000 8550 5100
Wire Wire Line
	8250 4600 8750 4600
Wire Wire Line
	8750 4600 8750 4700
Wire Wire Line
	8050 4800 8350 4800
Wire Wire Line
	8350 4800 8350 4500
Wire Wire Line
	8350 4500 8950 4500
Wire Wire Line
	8950 4500 8950 4700
Wire Wire Line
	8050 5100 8350 5100
Wire Wire Line
	8050 2700 8350 2700
Wire Wire Line
	8350 2700 8350 2500
Wire Wire Line
	8350 2500 8550 2500
Wire Wire Line
	8550 2700 8550 2600
Wire Wire Line
	8550 2600 8050 2600
Wire Wire Line
	8050 2400 8350 2400
Wire Wire Line
	8350 2400 8350 2100
Wire Wire Line
	8350 2100 8950 2100
Wire Wire Line
	8950 2100 8950 2300
Wire Wire Line
	8050 2300 8250 2300
Wire Wire Line
	8250 2300 8250 2200
Wire Wire Line
	8250 2200 8750 2200
Wire Wire Line
	8750 2200 8750 2300
$EndSCHEMATC
