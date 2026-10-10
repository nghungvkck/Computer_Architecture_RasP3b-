
import RPi.GPIO as GPIO
import time

# ==============================
# GPIO Configuration
# ==============================
SERVO = 6

BTS = {
    "BT_1": 21,
    "BT_2": 26,
    "BT_3": 20
}

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(SERVO, GPIO.OUT)

for pin in BTS.values():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Servo PWM: 50 Hz
pwm = GPIO.PWM(SERVO, 50)
pwm.start(0)


# ==============================
# Servo Control
# ==============================
def set_servo_angle(angle):
    # Convert angle to approximate duty cycle
    duty = 2.5 + (angle / 180.0) * 10.0

    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)

    # Stop sending active pulses after moving
    pwm.ChangeDutyCycle(0)


# ==============================
# Main Program
# ==============================
def main():
    while True:

        if GPIO.input(BTS["BT_1"]) == GPIO.LOW:
            time.sleep(0.05)  # Debounce

            if GPIO.input(BTS["BT_1"]) == GPIO.LOW:
                set_servo_angle(20)

                # Wait until the button is released
                while GPIO.input(BTS["BT_1"]) == GPIO.LOW:
                    time.sleep(0.01)

        elif GPIO.input(BTS["BT_2"]) == GPIO.LOW:
            time.sleep(0.05)

            if GPIO.input(BTS["BT_2"]) == GPIO.LOW:
                set_servo_angle(60)

                while GPIO.input(BTS["BT_2"]) == GPIO.LOW:
                    time.sleep(0.01)

        elif GPIO.input(BTS["BT_3"]) == GPIO.LOW:
            time.sleep(0.05)

            if GPIO.input(BTS["BT_3"]) == GPIO.LOW:
                set_servo_angle(160)

                while GPIO.input(BTS["BT_3"]) == GPIO.LOW:
                    time.sleep(0.01)

        time.sleep(0.02)


# ==============================
# Program Entry
# ==============================
try:
    main()

except KeyboardInterrupt:
    pass

finally:
    pwm.stop()
    GPIO.cleanup()
