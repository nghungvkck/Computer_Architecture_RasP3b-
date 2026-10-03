#===============================
#viet chuong trinh nhan nut bam 1 thi led sang
#nhan nut bam 2 thi led tat
#bam nut bam 3 thi led nhap nhay theo yeu cau 
#===============================

import RPi.GPIO as GPIO
import time

bt1 = 21
bt2 = 26
bt3 = 20
led = 13

state = "one"

GPIO.setmode(GPIO.BCM)

GPIO.setup(led, GPIO.OUT)
GPIO.setup(bt1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(bt2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(bt3, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def updateled(state):
    if state == "one":
        GPIO.output(led, GPIO.HIGH)
    elif state == "two":
        GPIO.output(led, GPIO.LOW)


try:
    while True:
        if GPIO.input(bt1) == GPIO.LOW:
            state = "one"
            updateled(state)

        if GPIO.input(bt2) == GPIO.LOW:
            state = "two"
            updateled(state)

        if GPIO.input(bt3) == GPIO.LOW:
            GPIO.output(led, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(led, GPIO.LOW)
            time.sleep(0.1)

except KeyboardInterrupt:
    GPIO.cleanup()