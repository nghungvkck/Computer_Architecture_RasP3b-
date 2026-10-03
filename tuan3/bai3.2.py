#=========================
# viet chuong tring nhan nut bam 1 lan 1 thi led sang, 
# nhan nut bam 1 lan 2 thi let tat 
# qua trinh nay lap di lap lai
#=========================

import RPi.GPIO as GPIO
import time
led= 13
button_1 = 11

GPIO.setup(GPIO.BCM)
GPIO.setup(button_1, GPIO.IN, pull_up_down= GPIO.PUD_UP)

dem = 1
def update(dem):
    if GPIO.input(button_1) and dem%2 == 1:
        GPIO.output(led, GPIO.HIGH)
    else:
        GPIO.output(led, GPIO.LOW)   
        time.sleep(0.25)
try:
    while True:
        update(dem=dem)
        dem+=1
except KeyboardInterrupt:
    GPIO.cleanup()