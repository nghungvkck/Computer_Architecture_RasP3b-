# Khởi tạo:
#     servo_goc = 90
#     dc_toc_do = 0
#     dc_chieu = 0 (0: dừng, 1: thuận, -1: nghịch)
#     Cập nhật phần cứng

# # Vòng lặp vô hạn:
#     Nếu Nút 1 được nhấn:
#         servo_goc = 60
#         dc_chieu = 1 (Thuận)
#         dc_toc_do = 60
#         Cập nhật Servo(60)
#         Cập nhật DC(60, Thuận)

#     Nếu Nút 2 được nhấn:
#         servo_goc = 120
#         dc_chieu = -1 (Nghịch)
#         dc_toc_do = 60
#         Cập nhật Servo(120)
#         Cập nhật DC(60, Nghịch)

#     Nếu Nút 3 được nhấn:
#         servo_goc = 90
#         dc_chieu = 0 (Dừng)
#         dc_toc_do = 0
#         Cập nhật Servo(90)
#         Cập nhật DC(0, Dừng)



import RPi.GPIO as GPIO
import time

# =============================
# GPIO CONFIGURATION
# =============================

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Push buttons
BT1 = 21
BT2 = 26
BT3 = 20

# RC-Servo
SERVO = 6

# DC motor
PWM_PIN = 24
DIR_PIN = 25

# LED
LED = 13

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
# GPIO SETUP
# =============================

for pin in LCD_PINS.values():
    GPIO.setup(pin, GPIO.OUT)

for button in [BT1, BT2, BT3]:
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(SERVO, GPIO.OUT)
GPIO.setup(PWM_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(LED, GPIO.OUT)

GPIO.output(LED, GPIO.LOW)

servo = GPIO.PWM(SERVO, 50)
servo.start(0)

dc_pwm = GPIO.PWM(PWM_PIN, 1000)
dc_pwm.start(0)

# =============================
# LCD FUNCTIONS
# =============================

def lcd_byte(bits, mode):
    GPIO.output(LCD_PINS['RS'], mode)

    # High nibble
    GPIO.output(LCD_PINS['D4'], bool(bits & 0x10))
    GPIO.output(LCD_PINS['D5'], bool(bits & 0x20))
    GPIO.output(LCD_PINS['D6'], bool(bits & 0x40))
    GPIO.output(LCD_PINS['D7'], bool(bits & 0x80))

    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)

    # Low nibble
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
    duty = 2.5 + (angle / 180.0) * 10.0
    servo.ChangeDutyCycle(duty)
    time.sleep(0.3)
    servo.ChangeDutyCycle(0)


# =============================
# DC MOTOR CONTROL
# =============================

def set_dc_motor(speed, direction):
    # Stop motor
    if direction == 0 or speed == 0:
        dc_pwm.ChangeDutyCycle(0)
        return

    # Set direction
    if direction == 1:
        GPIO.output(DIR_PIN, GPIO.HIGH)
    else:
        GPIO.output(DIR_PIN, GPIO.LOW)

    # Set motor speed
    dc_pwm.ChangeDutyCycle(speed)


# =============================
# UPDATE HARDWARE AND LCD
# =============================

def update_system(servo_angle, dc_speed, dc_direction):
    set_servo_angle(servo_angle)
    set_dc_motor(dc_speed, dc_direction)

    if dc_direction == 1:
        direction_text = "Forward"
    elif dc_direction == -1:
        direction_text = "Reverse"
    else:
        direction_text = "Stopped"

    lcd_display_string("Servo: {} deg".format(servo_angle), LCD_LINE_1)
    lcd_display_string("DC: {}% {}".format(dc_speed, direction_text),
                       LCD_LINE_2)


# =============================
# INITIAL STATE
# =============================

servo_angle = 90
dc_speed = 0
dc_direction = 0

try:
    lcd_init()

    update_system(servo_angle, dc_speed, dc_direction)

    previous_buttons = {
        BT1: GPIO.HIGH,
        BT2: GPIO.HIGH,
        BT3: GPIO.HIGH
    }

    # =============================
    # MAIN LOOP
    # =============================

    while True:
        current_buttons = {
            BT1: GPIO.input(BT1),
            BT2: GPIO.input(BT2),
            BT3: GPIO.input(BT3)
        }

        # Button 1: Forward
        if (previous_buttons[BT1] == GPIO.HIGH
                and current_buttons[BT1] == GPIO.LOW):

            servo_angle = 60
            dc_direction = 1
            dc_speed = 60

            GPIO.output(LED, GPIO.HIGH)
            update_system(servo_angle, dc_speed, dc_direction)

        # Button 2: Reverse
        elif (previous_buttons[BT2] == GPIO.HIGH
                and current_buttons[BT2] == GPIO.LOW):

            servo_angle = 120
            dc_direction = -1
            dc_speed = 60

            GPIO.output(LED, GPIO.HIGH)
            update_system(servo_angle, dc_speed, dc_direction)

        # Button 3: Stop and reset
        elif (previous_buttons[BT3] == GPIO.HIGH
                and current_buttons[BT3] == GPIO.LOW):

            servo_angle = 90
            dc_direction = 0
            dc_speed = 0

            GPIO.output(LED, GPIO.LOW)
            update_system(servo_angle, dc_speed, dc_direction)

        # Save button states
        previous_buttons = current_buttons.copy()

        # Turn LED off when no button is pressed
        if all(value == GPIO.HIGH for value in current_buttons.values()):
            GPIO.output(LED, GPIO.LOW)

        time.sleep(0.05)

except KeyboardInterrupt:
    pass

finally:
    dc_pwm.ChangeDutyCycle(0)
    servo.ChangeDutyCycle(0)

    dc_pwm.stop()
    servo.stop()

    GPIO.cleanup()
