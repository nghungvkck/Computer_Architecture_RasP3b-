
import RPi.GPIO as GPIO
import time

# ==============================
# GPIO Configuration
# ==============================
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

BUTTON_1 = 21
BUTTON_2 = 26

PWM_PIN = 24
DIR_PIN = 25

# ==============================
# GPIO Setup
# ==============================
GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(PWM_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(DIR_PIN, GPIO.OUT, initial=GPIO.LOW)

# ==============================
# PWM Configuration
# ==============================
pwm = GPIO.PWM(PWM_PIN, 1000)
pwm.start(0)

# ==============================
# Motor Control Variables
# ==============================
speed_levels = [0, 20, 40, 60]

speed_index = 0
speed = 0
direction = 0


def motor_control(speed, direction):
    """Set motor direction and PWM duty cycle."""

    GPIO.output(DIR_PIN, direction)
    pwm.ChangeDutyCycle(speed)


def change_motor(new_direction):
    """Increase speed and set motor direction."""

    global speed_index, speed, direction

    direction = new_direction

    speed_index = (speed_index + 1) % len(speed_levels)
    speed = speed_levels[speed_index]

    motor_control(speed, direction)

    direction_name = "Forward" if direction == 0 else "Reverse"

    print(f"Direction: {direction_name}")
    print(f"PWM Duty Cycle: {speed}%")
    print("-" * 30)


def main():
    """Main program loop."""

    global speed, speed_index, direction

    # Ensure the motor is stopped at startup
    speed = 0
    speed_index = 0
    direction = 0

    motor_control(0, 0)

    # Wait for both buttons to be released before starting
    while (
        GPIO.input(BUTTON_1) == GPIO.LOW
        or GPIO.input(BUTTON_2) == GPIO.LOW
    ):
        time.sleep(0.02)

    # Initialize previous button states
    previous_button_1 = GPIO.HIGH
    previous_button_2 = GPIO.HIGH

    print("System ready.")
    print("Motor stopped. Press a button to start.")

    while True:
        button_1 = GPIO.input(BUTTON_1)
        button_2 = GPIO.input(BUTTON_2)

        # Detect a new press on BUTTON_1
        if (
            previous_button_1 == GPIO.HIGH
            and button_1 == GPIO.LOW
        ):
            change_motor(0)

            # Debounce delay
            time.sleep(0.05)

        # Detect a new press on BUTTON_2
        elif (
            previous_button_2 == GPIO.HIGH
            and button_2 == GPIO.LOW
        ):
            change_motor(1)

            # Debounce delay
            time.sleep(0.05)

        # Update previous button states
        previous_button_1 = button_1
        previous_button_2 = button_2

        time.sleep(0.01)


try:
    main()

except KeyboardInterrupt:
    print("Stopping motor...")

finally:
    # Set PWM to zero before cleanup
    try:
        pwm.ChangeDutyCycle(0)
        pwm.stop()
    except Exception:
        pass

    GPIO.cleanup()
    print("GPIO cleanup completed.")
