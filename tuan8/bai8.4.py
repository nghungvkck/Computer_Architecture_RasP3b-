# Tóm tắt Logic Bài thực hành 4
# Phần cứng sử dụng:
# Động cơ RC-Servo.
# 3 nút bấm (Nút 1, Nút 2, Nút 3).
# Màn hình LCD 16x2.
# Logic hoạt động chi tiết:
# Trạng thái ban đầu:
# Khởi tạo động cơ RC-Servo ở vị trí 90 độ.
# Xử lý nút bấm 1 (Giảm góc):
# Mỗi lần nhấn nút 1, góc quay của động cơ sẽ giảm đi 10 độ.
# Điều kiện dừng: Khi góc quay giảm đến 10 độ thì dừng lại (không giảm thêm nữa dù có nhấn tiếp).
# Xử lý nút bấm 2 (Tăng góc):
# Mỗi lần nhấn nút 2, góc quay của động cơ sẽ tăng thêm 10 độ.
# Điều kiện dừng: Khi góc quay tăng đến 160 độ thì dừng lại (không tăng thêm nữa).
# Xử lý nút bấm 3 (Thiết lập lại):
# Khi nhấn nút 3, động cơ sẽ thiết lập góc quay trở về 90 độ (như trạng thái ban đầu).
# Hiển thị:
# Trong suốt quá trình hoạt động, giá trị góc quay hiện tại (số độ) luôn được hiển thị lên màn hình LCD 16x2.



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

# Servo settings
MIN_ANGLE = 10
MAX_ANGLE = 160
INITIAL_ANGLE = 90
ANGLE_STEP = 10

# =============================
# GPIO SETUP
# =============================

for pin in LCD_PINS.values():
    GPIO.setup(pin, GPIO.OUT)

for button in [BT1, BT2, BT3]:
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(SERVO, GPIO.OUT)

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
    duty = 2.5 + (angle / 180.0) * 10.0
    servo.ChangeDutyCycle(duty)

    # Allow the servo to move
    time.sleep(0.3)

    # Stop sending pulses until the next position update
    servo.ChangeDutyCycle(0)


# =============================
# UPDATE LCD
# =============================

def update_lcd(angle):
    lcd_display_string("Servo Control", LCD_LINE_1)
    lcd_display_string("Angle: {} deg".format(angle), LCD_LINE_2)


# =============================
# MAIN PROGRAM
# =============================

angle = INITIAL_ANGLE

try:
    lcd_init()

    # Set initial position
    set_servo_angle(angle)
    update_lcd(angle)

    # Previous button states
    previous_bt1 = GPIO.HIGH
    previous_bt2 = GPIO.HIGH
    previous_bt3 = GPIO.HIGH

    while True:
        current_bt1 = GPIO.input(BT1)
        current_bt2 = GPIO.input(BT2)
        current_bt3 = GPIO.input(BT3)

        changed = False

        # Button 3: Reset to 90 degrees
        if previous_bt3 == GPIO.HIGH and current_bt3 == GPIO.LOW:
            angle = INITIAL_ANGLE
            changed = True

        # Button 1: Decrease angle
        elif previous_bt1 == GPIO.HIGH and current_bt1 == GPIO.LOW:
            angle = max(MIN_ANGLE, angle - ANGLE_STEP)
            changed = True

        # Button 2: Increase angle
        elif previous_bt2 == GPIO.HIGH and current_bt2 == GPIO.LOW:
            angle = min(MAX_ANGLE, angle + ANGLE_STEP)
            changed = True

        if changed:
            set_servo_angle(angle)
            update_lcd(angle)

        previous_bt1 = current_bt1
        previous_bt2 = current_bt2
        previous_bt3 = current_bt3

        time.sleep(0.05)

except KeyboardInterrupt:
    pass

finally:
    servo.ChangeDutyCycle(0)
    servo.stop()
    GPIO.cleanup()