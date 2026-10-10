
import RPi.GPIO as GPIO
import time

# ==============================
# GPIO Configuration
# ==============================
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

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

BT1 = 21
SERVO = 6

GPIO.setup(BT1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SERVO, GPIO.OUT)

pwm = GPIO.PWM(SERVO, 50)


# ==============================
# LCD Functions
# ==============================
def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)

    GPIO.output(LCD_PINS['BL'], GPIO.HIGH)

    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)
    time.sleep(0.002)


def lcd_byte(bits, mode):
    GPIO.output(LCD_PINS['RS'], mode)

    # Send high nibble
    for bit_num in range(4):
        value = (bits >> (bit_num + 4)) & 1
        GPIO.output(LCD_PINS[f'D{bit_num + 4}'], value)

    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], GPIO.HIGH)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], GPIO.LOW)
    time.sleep(E_DELAY)

    # Send low nibble
    for bit_num in range(4):
        value = (bits >> bit_num) & 1
        GPIO.output(LCD_PINS[f'D{bit_num + 4}'], value)

    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], GPIO.HIGH)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], GPIO.LOW)
    time.sleep(E_DELAY)

    if mode == LCD_CMD and bits in (0x01, 0x02):
        time.sleep(0.002)


def lcd_clear():
    lcd_byte(0x01, LCD_CMD)


def lcd_display_string(message, line):
    address = LCD_LINE_1 if line == 1 else LCD_LINE_2
    lcd_byte(address, LCD_CMD)

    # Limit the message to 16 characters
    message = str(message)[:LCD_WIDTH].ljust(LCD_WIDTH)

    for char in message:
        lcd_byte(ord(char), LCD_CHR)


# ==============================
# Servo Control
# ==============================
def set_servo_angle(angle):
    # Approximate servo range: 0 to 180 degrees
    duty = 2.5 + (angle / 180.0) * 10.0

    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)


# ==============================
# Main Program
# ==============================
def main():
    cur_angle = 0

    pwm.start(0)
    lcd_init()

    lcd_display_string("Servo ready", 1)
    lcd_display_string("Angle: 0 deg", 2)

    while True:
        if GPIO.input(BT1) == GPIO.LOW:
            time.sleep(0.05)  # Debounce

            if GPIO.input(BT1) == GPIO.LOW:
                cur_angle += 10

                if cur_angle > 160:
                    cur_angle = 10

                set_servo_angle(cur_angle)

                lcd_display_string("Servo position", 1)
                lcd_display_string(f"Angle: {cur_angle} deg", 2)

                # Wait for button release
                while GPIO.input(BT1) == GPIO.LOW:
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
