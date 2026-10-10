# Khởi tạo:
#     Cấu hình chân cho Cảm biến ánh sáng (LIGHT_SS), Rơ-le 1 (RELAY_1), Rơ-le 2 (RELAY_2).
#     Khởi tạo màn hình LCD 16x2.
#     Đặt trạng thái ban đầu cho các Rơ-le là TẮT (OFF).

# Vòng lặp vô hạn:
#     Đọc giá trị từ Cảm biến ánh sáng.

#     Nếu Cảm biến báo SÁNG:
#         Tắt Rơ-le 1.
#         Tắt Rơ-le 2.
#         Hiển thị LCD: "Troi Sang", "RL1: TAT", "RL2: TAT".

#     Ngược lại (Cảm biến báo TỐI):
#         Bật Rơ-le 1.
#         Hiển thị LCD: "Troi Toi", "RL1: BAT", "RL2: TAT".
        
#         Chờ 3 giây (time.sleep(3)).
        
#         Bật Rơ-le 2.
#         Hiển thị LCD: "Troi Toi", "RL1: BAT", "RL2: BAT".

#     Chờ một khoảng thời gian ngắn (ví dụ 0.1s) để ổn định vòng lặp.




import RPi.GPIO as GPIO
import time

# =============================
# GPIO CONFIGURATION
# =============================

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Light sensor
LIGHT_SS = 5

# Relay pins
RELAY_1 = 16
RELAY_2 = 12

# LCD pins
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
# LCD FUNCTIONS
# =============================

def lcd_byte(bits, mode):
    GPIO.output(LCD_PINS['RS'], mode)

    # Send high nibble
    for bit_num in range(4):
        pin = LCD_PINS[f'D{bit_num + 4}']
        GPIO.output(
            pin,
            (bits & (1 << (bit_num + 4))) != 0
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


def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)

    GPIO.output(LCD_PINS['BL'], GPIO.HIGH)
    time.sleep(0.05)

    for command in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
        lcd_byte(command, LCD_CMD)
        time.sleep(0.002)


def lcd_display_string(message, line):
    if line == 1:
        lcd_byte(LCD_LINE_1, LCD_CMD)
    elif line == 2:
        lcd_byte(LCD_LINE_2, LCD_CMD)
    else:
        return

    message = message.ljust(LCD_WIDTH)[:LCD_WIDTH]

    for char in message:
        lcd_byte(ord(char), LCD_CHR)


# =============================
# MAIN PROGRAM
# =============================

def main():
    # Configure input and output pins
    GPIO.setup(
        LIGHT_SS,
        GPIO.IN,
        pull_up_down=GPIO.PUD_UP
    )

    GPIO.setup(RELAY_1, GPIO.OUT)
    GPIO.setup(RELAY_2, GPIO.OUT)

    # Initialize relays to OFF
    GPIO.output(RELAY_1, GPIO.LOW)
    GPIO.output(RELAY_2, GPIO.LOW)

    # Initialize LCD
    lcd_init()

    while True:
        light_state = GPIO.input(LIGHT_SS)

        # Light detected
        if light_state == GPIO.LOW:
            GPIO.output(RELAY_1, GPIO.LOW)
            GPIO.output(RELAY_2, GPIO.LOW)

            lcd_display_string("Troi Sang", 1)
            lcd_display_string("RL1: TAT RL2:TAT", 2)

        # Dark detected
        else:
            # Turn on Relay 1
            GPIO.output(RELAY_1, GPIO.HIGH)
            GPIO.output(RELAY_2, GPIO.LOW)

            lcd_display_string("Troi Toi", 1)
            lcd_display_string("RL1: BAT RL2:TAT", 2)

            # Wait 3 seconds before activating Relay 2
            time.sleep(3)

            # Turn on Relay 2
            GPIO.output(RELAY_2, GPIO.HIGH)

            lcd_display_string("Troi Toi", 1)
            lcd_display_string("RL1: BAT RL2:BAT", 2)

        time.sleep(0.1)


# =============================
# PROGRAM ENTRY POINT
# =============================

try:
    lcd_init()
    main()

except KeyboardInterrupt:
    pass

finally:
    # Turn off relays before exiting
    GPIO.output(RELAY_1, GPIO.LOW)
    GPIO.output(RELAY_2, GPIO.LOW)

    GPIO.cleanup()
