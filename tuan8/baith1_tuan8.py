
import RPi.GPIO as GPIO
import time

# =============================
# GPIO CONFIGURATION
# =============================

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

BT1 = 21
SERVO = 6
LED = 13

LCD_PINS = {
    'RS': 23,
    'E': 27,
    'D4': 18,
    'D5': 17,
    'D6': 14,
    'D7': 3,
    'BL': 2
}

LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0

E_PULSE = 0.0005
E_DELAY = 0.0005

# =============================
# SERVO CONFIGURATION
# =============================

INITIAL_ANGLE = 30
ANGLE_STEP = 10
MAX_ANGLE = 180

# =============================
# GPIO SETUP
# =============================

GPIO.setup(BT1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SERVO, GPIO.OUT)
GPIO.setup(LED, GPIO.OUT)

for pin in LCD_PINS.values():
    GPIO.setup(pin, GPIO.OUT)

GPIO.output(LED, GPIO.LOW)

servo = GPIO.PWM(SERVO, 50)
servo.start(0)

# =============================
# LCD FUNCTIONS
# =============================

def lcd_byte(bits, mode):
    GPIO.output(LCD_PINS['RS'], mode)

    # Send high nibble
    GPIO.output(LCD_PINS['D4'], bool(bits & 0x10))
    GPIO.output(LCD_PINS['D5'], bool(bits & 0x20))
    GPIO.output(LCD_PINS['D6'], bool(bits & 0x40))
    GPIO.output(LCD_PINS['D7'], bool(bits & 0x80))

    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)

    # Send low nibble
    GPIO.output(LCD_PINS['D4'], bool(bits & 0x01))
    GPIO.output(LCD_PINS['D5'], bool(bits & 0x02))
    GPIO.output(LCD_PINS['D6'], bool(bits & 0x04))
    GPIO.output(LCD_PINS['D7'], bool(bits & 0x08))

    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)


def lcd_init():
    GPIO.output(LCD_PINS['BL'], True)
    time.sleep(0.05)

    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)

    time.sleep(0.002)


def lcd_display_string(message, line):
    message = message.ljust(LCD_WIDTH)[:LCD_WIDTH]
    lcd_byte(line, LCD_CMD)

    for char in message:
        lcd_byte(ord(char), LCD_CHR)


# =============================
# SERVO CONTROL
# =============================

def set_servo_angle(angle):
    # Approximate duty cycle for a 0-180 degree servo
    duty = 2.5 + (angle / 180.0) * 10.0

    servo.ChangeDutyCycle(duty)
    time.sleep(0.3)
    servo.ChangeDutyCycle(0)


# =============================
# LCD DISPLAY
# =============================

def update_lcd(angle):
    lcd_display_string("RC Servo Control", LCD_LINE_1)
    lcd_display_string("Angle: {} deg".format(angle), LCD_LINE_2)


# =============================
# MAIN PROGRAM
# =============================

angle = INITIAL_ANGLE

try:
    lcd_init()

    # Move servo to the initial angle
    set_servo_angle(angle)
    update_lcd(angle)

    previous_button = GPIO.HIGH

    while True:
        current_button = GPIO.input(BT1)

        # Detect a new button press
        if previous_button == GPIO.HIGH and current_button == GPIO.LOW:
            # Turn LED on when the button is pressed
            GPIO.output(LED, GPIO.HIGH)

            # Increase servo angle by 10 degrees
            angle = min(angle + ANGLE_STEP, MAX_ANGLE)

            set_servo_angle(angle)
            update_lcd(angle)

        # Turn LED off when the button is released
        if current_button == GPIO.HIGH:
            GPIO.output(LED, GPIO.LOW)

        previous_button = current_button
        time.sleep(0.05)

except KeyboardInterrupt:
    pass

finally:
    GPIO.output(LED, GPIO.LOW)
    servo.stop()
    GPIO.cleanup()
