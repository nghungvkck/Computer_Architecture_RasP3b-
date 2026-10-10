import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
pwm_Pin = 24
dir_Pin = 25
GPIO.setup(pwm_Pin, GPIO.OUT)
GPIO.setup(dir_Pin, GPIO.OUT)
pwn = GPIO.PWM(pwm_Pin, 1000)
pwn.start(0)
def motor_control(speed,direction):
    GPIO.output(dir_Pin, direction)
    pwn.ChangeDutyCycle(speed)
def main():
    while True:
        motor_control(50,0)
try:
    main()
except KeyboardInterrupt:
    pwn.stop()
    GPIO.cleanup()