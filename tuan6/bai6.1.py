import RPi.GPIO as GPIO
import time

# =============================
# PIN CONFIGURATION
# =============================
RLS = {
    'RELAY_1': 16,
    'RELAY_2': 12,
    'LED': 13
}

LCD_PINS = {
    'RS': 23,
    'E': 27,
    'D4': 18,
    'D5': 17,
    'D6': 14,
    'D7': 3,
    'BL': 2
}

DHT11_PIN = 7

LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0

E_PULSE = 0.0005
E_DELAY = 0.0005

ROOM_TEMPERATURE = 25

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


# =============================
# LCD FUNCTIONS
# =============================
def lcd_byte(bits, mode):
    GPIO.output(LCD_PINS['RS'], mode)

    # Send higher 4 bits
    for bit_num in range(4):
        value = (bits >> (bit_num + 4)) & 1
        GPIO.output(LCD_PINS[f'D{bit_num + 4}'], value)

    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], GPIO.HIGH)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], GPIO.LOW)
    time.sleep(E_DELAY)

    # Send lower 4 bits
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


def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)

    GPIO.output(LCD_PINS['RS'], GPIO.LOW)
    GPIO.output(LCD_PINS['E'], GPIO.LOW)

    time.sleep(0.05)

    # Initialize LCD in 4-bit mode
    for _ in range(3):
        for name in ('D4', 'D5', 'D6', 'D7'):
            GPIO.output(LCD_PINS[name], GPIO.LOW)

        GPIO.output(LCD_PINS['D4'], GPIO.HIGH)
        GPIO.output(LCD_PINS['D5'], GPIO.HIGH)

        GPIO.output(LCD_PINS['E'], GPIO.HIGH)
        time.sleep(E_PULSE)
        GPIO.output(LCD_PINS['E'], GPIO.LOW)
        time.sleep(0.005)

    # Switch to 4-bit mode
    for name in ('D4', 'D5', 'D6', 'D7'):
        GPIO.output(LCD_PINS[name], GPIO.LOW)

    GPIO.output(LCD_PINS['D5'], GPIO.HIGH)
    GPIO.output(LCD_PINS['E'], GPIO.HIGH)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], GPIO.LOW)
    time.sleep(E_DELAY)

    lcd_byte(0x28, LCD_CMD)  # 4-bit, 2 lines
    lcd_byte(0x0C, LCD_CMD)  # Display ON
    lcd_byte(0x06, LCD_CMD)  # Cursor increment
    lcd_byte(0x01, LCD_CMD)  # Clear display


def lcd_clear():
    lcd_byte(0x01, LCD_CMD)


def lcd_display_string(message, line):
    address = LCD_LINE_1 if line == 1 else LCD_LINE_2
    lcd_byte(address, LCD_CMD)

    message = str(message)[:LCD_WIDTH].ljust(LCD_WIDTH)

    for char in message:
        lcd_byte(ord(char), LCD_CHR)


# =============================
# DHT11 READING
# =============================
def wait_for_level(level, timeout=0.005):
    start = time.monotonic()

    while GPIO.input(DHT11_PIN) != level:
        if time.monotonic() - start > timeout:
            return False

    return True


def read_dht11():
    # Send start signal
    GPIO.setup(DHT11_PIN, GPIO.OUT)
    GPIO.output(DHT11_PIN, GPIO.LOW)
    time.sleep(0.018)

    GPIO.output(DHT11_PIN, GPIO.HIGH)
    time.sleep(0.00003)

    GPIO.setup(DHT11_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Wait for sensor response
    if not wait_for_level(GPIO.LOW):
        return None, None

    if not wait_for_level(GPIO.HIGH):
        return None, None

    if not wait_for_level(GPIO.LOW):
        return None, None

    data = []

    # Read 40 data bits
    for _ in range(40):
        if not wait_for_level(GPIO.HIGH):
            return None, None

        start = time.monotonic()

        if not wait_for_level(GPIO.LOW):
            return None, None

        pulse_length = time.monotonic() - start

        # NOTE: pulse timing must be validated on the
        # actual hardware/simulator.
        data.append(1 if pulse_length > 0.00004 else 0)

    # Convert bits into 5 bytes
    values = []

    for i in range(0, 40, 8):
        value = 0

        for bit in data[i:i + 8]:
            value = (value << 1) | bit

        values.append(value)

    humidity_int = values[0]
    humidity_dec = values[1]
    temperature_int = values[2]
    temperature_dec = values[3]
    checksum = values[4]

    expected_checksum = (
        humidity_int + humidity_dec
        + temperature_int + temperature_dec
    ) & 0xFF

    if checksum != expected_checksum:
        return None, None

    temperature = temperature_int + temperature_dec
    humidity = humidity_int + humidity_dec

    return temperature, humidity


# =============================
# DEVICE CONTROL
# =============================
def control_devices(temperature):
    if temperature > ROOM_TEMPERATURE:
        GPIO.output(RLS['RELAY_1'], GPIO.HIGH)
        GPIO.output(RLS['RELAY_2'], GPIO.HIGH)
        GPIO.output(RLS['LED'], GPIO.HIGH)

    elif temperature == ROOM_TEMPERATURE:
        GPIO.output(RLS['RELAY_1'], GPIO.HIGH)
        GPIO.output(RLS['RELAY_2'], GPIO.LOW)
        GPIO.output(RLS['LED'], GPIO.LOW)

    else:
        GPIO.output(RLS['RELAY_1'], GPIO.LOW)
        GPIO.output(RLS['RELAY_2'], GPIO.LOW)
        GPIO.output(RLS['LED'], GPIO.LOW)


# =============================
# MAIN PROGRAM
# =============================
def main():
    # Initialize output pins
    for pin in RLS.values():
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

    lcd_init()

    GPIO.output(LCD_PINS['BL'], GPIO.HIGH)

    lcd_display_string("DHT11 System", 1)
    lcd_display_string("Initializing...", 2)
    time.sleep(2)

    while True:
        temperature, humidity = read_dht11()

        if temperature is None or humidity is None:
            print("DHT11 read error")

            lcd_display_string("Sensor Error", 1)
            lcd_display_string("Check Sensor", 2)

            # Safe state on invalid readings
            for pin in RLS.values():
                GPIO.output(pin, GPIO.LOW)

            time.sleep(2)
            continue

        print(
            "Temperature: {} C, Humidity: {} %".format(
                temperature, humidity
            )
        )

        lcd_display_string(
            "Temp: {} C".format(temperature), 1
        )
        lcd_display_string(
            "Humidity: {} %".format(humidity), 2
        )

        control_devices(temperature)

        # DHT11 should not be read too frequently
        time.sleep(2)


# =============================
# PROGRAM ENTRY
# =============================
try:
    main()

except KeyboardInterrupt:
    pass

finally:
    try:
        for pin in RLS.values():
            GPIO.output(pin, GPIO.LOW)

        lcd_clear()

    except Exception:
        pass

    GPIO.cleanup()