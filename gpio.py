#!/usr/bin/env python
import subprocess
import RPi.GPIO as GPIO
import time

# BCM-Numbering.
GPIO.setmode(GPIO.BCM)

GPIO.setup(20, GPIO.IN)
monitor_out_name = "HDMI-A-1"
montion_detected = False
while 1 == 1:
    sensor_value = GPIO.input(20)
    montion_detected =  sensor_value == 0

    if montion_detected:
        print("Person detected")
        #subprocess.run(f"wlr-randr --output \"{monitor_out_name}\" --on",check=True, shell=True)
    else:
        print(".")
        #subprocess.run(f"wlr-randr --output \"{monitor_out_name}\" --off",check=True, shell=True)
    
    
    time.sleep(0.01)

# Free
GPIO.cleanup()