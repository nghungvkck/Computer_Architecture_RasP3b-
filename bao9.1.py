
import RPi.GPIO as GPIO
import time

# =============================
# LCD CONFIGURATION
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

LCD_WIDTH = 16

LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0

E_PULSE = 0.0005
E_DELAY = 0.0005

# Light sensor input
LIGHT_SS = 5

# =============================
# GPIO INITIALIZATION
# =============================

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


# =============================
# LCD FUNCTIONS
# =============================

def lcd_byte(bits, mode):
    GPIO.output(LCD_PINS['RS'], mode)

    # Send high nibble
    for bit_num in range(4):
        pin = LCD_PINS[f'D{bit_num + 4}']
        GPIO.output(
            pin,
            (bits & (1 << (4 + bit_num))) != 0
        )

    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)

    # Send low nibble
    for bit_num in range(4):
        pin = LCD_PINS[f'D{bit_num + 4}']
        GPIO.output(
            pin,
            (bits & (1 << bit_num)) != 0
        )

    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)

    # Commands that clear or return home need extra time
    if mode == LCD_CMD and bits in (0x01, 0x02):
        time.sleep(0.002)


def lcd_init():
    # Configure LCD pins
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)

    # Turn on LCD backlight
    GPIO.output(LCD_PINS['BL'], GPIO.HIGH)

    # Wait for LCD power-up
    time.sleep(0.05)

    # Initialize LCD in 4-bit mode
    for byte in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
        lcd_byte(byte, LCD_CMD)
        time.sleep(0.002)


def lcd_clear():
    lcd_byte(0x01, LCD_CMD)
    time.sleep(0.002)


def lcd_display_string(message, line):
    # Select LCD line
    if line == 1:
        lcd_byte(LCD_LINE_1, LCD_CMD)
    elif line == 2:
        lcd_byte(LCD_LINE_2, LCD_CMD)
    else:
        return

    # Fill the line to remove leftover characters
    message = message.ljust(LCD_WIDTH)[:LCD_WIDTH]

    for char in message:
        lcd_byte(ord(char), LCD_CHR)


# =============================
# MAIN PROGRAM
# =============================

def main():
    lcd_init()

    # Configure light sensor input
    GPIO.setup(
        LIGHT_SS,
        GPIO.IN,
        pull_up_down=GPIO.PUD_UP
    )

    lcd_display_string("Light Sensor", 1)
    lcd_display_string("Initializing...", 2)
    time.sleep(1)

    previous_state = None

    while True:
        # Read sensor state
        current_state = GPIO.input(LIGHT_SS)

        # Update LCD only when the state changes
        if current_state != previous_state:
            if current_state == GPIO.LOW:
                lcd_display_string("Sang", 1)
                lcd_display_string("Light detected", 2)
            else:
                lcd_display_string("Toi", 1)
                lcd_display_string("No light", 2)

            previous_state = current_state

        time.sleep(0.1)


# =============================
# PROGRAM ENTRY POINT
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
