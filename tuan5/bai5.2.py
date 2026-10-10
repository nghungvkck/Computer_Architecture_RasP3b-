```python
import RPi.GPIO as GPIO
import time

# =============================
# LCD Configuration
# =============================
LCD_PINS = {
    'RS': 23,
    'E': 27,
    'D4': 18,
    'D5': 17,
    'D6': 14,
    'D7': 3,
    'BL': 2
}

BT_1 = 21

LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0

E_PULSE = 0.0005
E_DELAY = 0.0005

MESSAGE = "Hello-World!"


# =============================
# GPIO Initialization
# =============================
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

for pin in LCD_PINS.values():
    GPIO.setup(pin, GPIO.OUT)

# Button connected between GPIO 21 and GND
GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# =============================
# Send Data to LCD
# =============================
def lcd_byte(bits, mode):
    GPIO.output(LCD_PINS['RS'], mode)

    # Send higher 4 bits
    for bit_num in range(4):
        bit_value = (bits >> (bit_num + 4)) & 1
        GPIO.output(
            LCD_PINS[f'D{bit_num + 4}'],
            bit_value
        )

    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)

    # Send lower 4 bits
    for bit_num in range(4):
        bit_value = (bits >> bit_num) & 1
        GPIO.output(
            LCD_PINS[f'D{bit_num + 4}'],
            bit_value
        )

    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)

    # Clear and return home need extra execution time
    if mode == LCD_CMD and bits in (0x01, 0x02):
        time.sleep(0.002)


# =============================
# Initialize LCD
# =============================
def lcd_init():
    time.sleep(0.05)

    # Initialize LCD in 4-bit mode
    GPIO.output(LCD_PINS['RS'], False)
    GPIO.output(LCD_PINS['E'], False)

    for _ in range(3):
        for bit_num in range(4):
            GPIO.output(LCD_PINS[f'D{bit_num + 4}'], False)

        # Send initialization nibble 0x3
        GPIO.output(LCD_PINS['D4'], True)
        GPIO.output(LCD_PINS['D5'], True)

        GPIO.output(LCD_PINS['E'], True)
        time.sleep(E_PULSE)
        GPIO.output(LCD_PINS['E'], False)
        time.sleep(0.005)

    # Switch to 4-bit mode using nibble 0x2
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num + 4}'], False)

    GPIO.output(LCD_PINS['D5'], True)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)

    # Configure LCD
    lcd_byte(0x28, LCD_CMD)  # 4-bit, 2 lines, 5x8 font
    lcd_byte(0x0C, LCD_CMD)  # Display ON, cursor OFF
    lcd_byte(0x06, LCD_CMD)  # Increment cursor
    lcd_byte(0x01, LCD_CMD)  # Clear display


# =============================
# LCD Display Functions
# =============================
def lcd_clear():
    lcd_byte(0x01, LCD_CMD)


def lcd_display_string(message, line=1):
    address = LCD_LINE_1 if line == 1 else LCD_LINE_2

    lcd_byte(address, LCD_CMD)

    # Keep text within LCD width
    message = message[:LCD_WIDTH]

    for char in message:
        lcd_byte(ord(char), LCD_CHR)


# =============================
# Button Press Detection
# =============================
def wait_for_button_release():
    while GPIO.input(BT_1) == GPIO.LOW:
        time.sleep(0.01)


def wait_for_button_press():
    while True:
        if GPIO.input(BT_1) == GPIO.LOW:
            time.sleep(0.03)  # Debounce

            if GPIO.input(BT_1) == GPIO.LOW:
                wait_for_button_release()
                time.sleep(0.03)
                return

        time.sleep(0.01)


# =============================
# Text Animation
# =============================
def move_left_to_right():
    max_position = LCD_WIDTH - len(MESSAGE)

    for position in range(max_position + 1):
        lcd_clear()
        lcd_display_string(" " * position + MESSAGE, 1)
        time.sleep(0.25)


def move_right_to_left():
    max_position = LCD_WIDTH - len(MESSAGE)

    for position in range(max_position, -1, -1):
        lcd_clear()
        lcd_display_string(" " * position + MESSAGE, 1)
        time.sleep(0.25)


# =============================
# Main Program
# =============================
def main():
    lcd_init()

    # Set LOW here if the simulated backlight circuit is active-low.
    # Set HIGH if the circuit is active-high.
    GPIO.output(LCD_PINS['BL'], True)

    lcd_clear()
    lcd_display_string("Press button", 1)
    lcd_display_string("to start", 2)

    state = 0

    while True:
        wait_for_button_press()

        state += 1

        if state == 1:
            move_left_to_right()

        elif state == 2:
            move_right_to_left()

        else:
            lcd_clear()
            lcd_display_string("Press button", 1)
            lcd_display_string("to start", 2)
            state = 0


# =============================
# Program Entry
# =============================
try:
    main()

except KeyboardInterrupt:
    pass

finally:
    try:
        lcd_clear()
    except Exception:
        pass

    GPIO.cleanup()
```