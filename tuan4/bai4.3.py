import RPi.GPIO as GPIO
import time
bt1 = 21
bt2 = 26
relay_1 = 16
relay_2 = 12

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(bt1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(bt2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(relay_1, GPIO.OUT)
GPIO.setup(relay_2, GPIO.OUT)

def main():
    while True:
        if GPIO.input(bt1) == GPIO.LOW:
            GPIO.output(relay_1, GPIO.HIGH)
            GPIO.output(relay_2, GPIO.LOW)
            print("Button 1 pressed")
            time.sleep(0.25)
        if GPIO.input(bt2) == GPIO.LOW:
            GPIO.output(relay_1, GPIO.LOW)
            GPIO.output(relay_2, GPIO.HIGH)
            print("Button 1 pressed")
            time.sleep(0.25)
try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
