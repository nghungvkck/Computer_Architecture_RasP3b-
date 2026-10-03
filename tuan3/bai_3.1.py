#==========================
# chuong trinh bam nut 1 thi phat sang
# tha nut 1 thi den tat
#==========================

import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
led = 13
Button_1= 21

GPIO.setup(led, GPIO.output)
GPIO.setup(Button_1, GPIO.IN, pull_up_down= GPIO.PUD_UP)   # kich hoat tro treo noi bo cua ras

def updateLed():
    # if GPIO.input(Button_1) == GPIO.LOW:
    if GPIO.input(Button_1):
        GPIO.output(led, GPIO.HIGH)
    else:
        GPIO.output(led, GPIO.LOW)
try:
    while True:
        updateLed()
except KeyboardInterrupt:
    GPIO.cleanup()


