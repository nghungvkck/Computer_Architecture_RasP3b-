
#=============================
# Dieu khien dong co DC quay mot chieu
# Toc do bang 50% toc do toi da
#=============================

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

PWM_PIN = 24
DIR_PIN = 25

GPIO.setup(PWM_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)

pwm = GPIO.PWM(PWM_PIN, 1000)
pwm.start(0)

def motor_control(speed, direction):
    GPIO.output(DIR_PIN, direction)
    pwm.ChangeDutyCycle(speed)

def main():
    motor_control(50, 0)

    while True:
        time.sleep(0.01)

try:
    main()

except KeyboardInterrupt:
    pass

finally:
    pwm.stop()
    GPIO.cleanup()