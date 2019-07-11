# -*- coding: utf-8 -*-

''' ###################### 
    A simple GPIO-based Controller for the Raspberry Pi (4B)

    # INSTRUCTIONS:
        Just plug in your fan to GROUND, 5V and PIN 2.
        Put a CIRCUIT before it with one RESISTOR (1k Ohm) and a TRANSISTOR.
        -> READY!

'''

import os
import sys
import time
import signal
import RPi.GPIO as GPIO

pin = 2                                 # The pin ID, edit here to change it
maxTMP = 60                             # The maximum temperature in Celsius after which we trigger the fan
cooldownTMP = 40
HIGHEST_TMP = 0.0                       # A variable for storing the max temperature
LOWEST_TMP = 0.0                        # A variable for storing the min temperature
FAN_STATE = ""

FOLDER = "/home/pi/scripts/python/"
file_high = FOLDER + "highest.txt"
file_low = FOLDER + "lowest.txt"


def setup():
    print("****   STARTING FAN CONTROLLER   ****\n\n")
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(pin, GPIO.OUT)
    global HIGHEST_TMP
    HIGHEST_TMP = loadTemperature(file_high)
    print("[ INFO ] Highest temperature ever measured:\t %.2f°C" % HIGHEST_TMP)
    global LOWEST_TMP
    LOWEST_TMP = loadTemperature(file_low)
    print("[ INFO ] Lowest temperature ever measured:\t %.2f°C\n" % LOWEST_TMP)
    fanON()
    return()


def loadTemperature(file):
    txt_file = open(file, 'r')
    return float(txt_file.readline())


def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    temp = (res.replace("temp=","").replace("'C\n",""))
    return temp


def fanON():
    setPin(True)
    global FAN_STATE
    FAN_STATE = "ON"
    return()


def fanOFF():
    setPin(False)
    global FAN_STATE
    FAN_STATE = "OFF"
    return()


# SET HISTORY OF TEMPS:
def checkMaxMin(tmp):
    global HIGHEST_TMP
    global LOWEST_TMP

    if tmp > HIGHEST_TMP:
        HIGHEST_TMP = tmp
        saveHighest(tmp)

    if tmp < LOWEST_TMP:
        LOWEST_TMP = tmp
        saveLowest(tmp)


def saveHighest(temperature):
    highestRecords = open(file_high, 'w')
    highestRecords.write(str(temperature))
    highestRecords.close()


def saveLowest(temperature):
    lowestRecords = open(file_low, 'w')
    lowestRecords.write(str(temperature))
    lowestRecords.close()


def getTEMP():
    CPU_temp = float(getCPUtemperature())

    if CPU_temp >= maxTMP:
        fanON()
    elif CPU_temp < cooldownTMP:
        fanOFF()

    checkMaxMin(CPU_temp)

    sys.stdout.write("\r[ STATUS : %s ] Current TEMP: %.2f°C | LOW: %.2f°C | HIGH: %.2f°C" % (FAN_STATE, CPU_temp, LOWEST_TMP, HIGHEST_TMP))
    sys.stdout.flush()
    return()


def setPin(mode):               # A little redundant function but useful if you want to add logging
    GPIO.output(pin, mode)
    return()

try:
    setup()

    while True:
        getTEMP()
        time.sleep(5)           # Read temp every 5sec
except KeyboardInterrupt:       # trap a CTRL+C keyboard interrupt
    print("\n\n[EXIT] SHUTTING DOWN....")
    GPIO.cleanup()              # resets all GPIO ports used by this program
