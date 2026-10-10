# Trạng thái ban đầu:
# Động cơ dừng yên.
# Xử lý nút bấm 1 (BT1):
# Khi nhấn và giữ: Động cơ quay theo chiều thuận. Tốc độ sẽ tăng dần 10% mỗi giây cho đến khi đạt 100%, sau đó duy trì ở mức 100%.
# Khi thả nút: Động cơ vẫn quay theo chiều thuận nhưng tốc độ sẽ giảm dần 10% mỗi giây cho đến khi dừng hẳn (0%).
# (Lưu ý: Sách in có lỗi chính tả ở đoạn này, ghi là "đạt đến tốc độ 100% thì duy trì" ở phần giảm tốc, nhưng logic đúng phải là giảm về 0%).
# Xử lý nút bấm 2 (BT2):
# Khi nhấn và giữ: Động cơ quay theo chiều ngược lại. Tốc độ cũng tăng dần 10% mỗi giây đến tối đa 100% và giữ nguyên.
# Khi thả nút: Động cơ vẫn quay chiều ngược nhưng tốc độ giảm dần 10% mỗi giây cho đến khi dừng hẳn.
# (Lưu ý: Sách cũng có lỗi tương tự ở đoạn này).
# Xử lý nút bấm 3 (BT3):
# Bất kể động cơ đang chạy ở trạng thái nào, khi nhấn nút này, động cơ sẽ dừng lại ngay lập tức.
# Hiển thị LCD:
# Màn hình LCD 16x2 sẽ hiển thị liên tục 2 thông tin: Chiều quay hiện tại và Tốc độ hiện tại của động cơ.


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

BT1 = 21
BT2 = 26
BT3 = 20

PWM_PIN = 24
DIR_PIN = 25

LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0

E_PULSE = 0.0005
E_DELAY = 0.0005

SPEED_STEP = 10
SPEED_INTERVAL = 1.0

# ==============================
# GPIO Setup
# ==============================
GPIO.setup(PWM_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)

for button in [BT1, BT2, BT3]:
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

pwm = GPIO.PWM(PWM_PIN, 1000)
pwm.start(0)

speed = 0
direction = 0
last_update = time.monotonic()


# ==============================
# LCD Functions
# ==============================
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


def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)

    GPIO.output(LCD_PINS['BL'], GPIO.HIGH)

    time.sleep(0.05)

    for command in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
        lcd_byte(command, LCD_CMD)


def lcd_display_string(message, line):
    address = LCD_LINE_1 if line == 1 else LCD_LINE_2
    lcd_byte(address, LCD_CMD)

    message = str(message)[:LCD_WIDTH].ljust(LCD_WIDTH)

    for char in message:
        lcd_byte(ord(char), LCD_CHR)


# ==============================
# Motor Control
# ==============================
def motor_control(new_speed, new_direction):
    global speed, direction

    speed = max(0, min(100, new_speed))
    direction = new_direction

    GPIO.output(DIR_PIN, direction)
    pwm.ChangeDutyCycle(speed)


def update_lcd():
    if speed == 0:
        status = "Motor stopped"
    elif direction == 0:
        status = "Forward"
    else:
        status = "Reverse"

    lcd_display_string(status, 1)
    lcd_display_string(f"Speed: {speed:3d}%", 2)


# ==============================
# Main Program
# ==============================
def main():
    global speed, direction, last_update

    lcd_init()
    motor_control(0, 0)
    update_lcd()

    while True:
        bt1 = GPIO.input(BT1) == GPIO.LOW
        bt2 = GPIO.input(BT2) == GPIO.LOW
        bt3 = GPIO.input(BT3) == GPIO.LOW

        now = time.monotonic()

        # BT3: Stop immediately
        if bt3:
            motor_control(0, direction)
            last_update = now
            update_lcd()
            time.sleep(0.05)
            continue

        # If BT1 and BT2 are pressed together, stop
        if bt1 and bt2:
            motor_control(0, direction)
            last_update = now
            update_lcd()
            time.sleep(0.05)
            continue

        # Select direction
        if bt1:
            direction = 0
        elif bt2:
            direction = 1

        # Adjust speed every second
        if now - last_update >= SPEED_INTERVAL:
            if bt1 or bt2:
                # Increase speed while the button is held
                speed = min(speed + SPEED_STEP, 100)
            else:
                # Reduce speed after releasing the button
                speed = max(speed - SPEED_STEP, 0)

            motor_control(speed, direction)
            last_update = now

        update_lcd()
        time.sleep(0.05)


# ==============================
# Program Entry
# ==============================
try:
    main()

except KeyboardInterrupt:
    pass

finally:
    pwm.ChangeDutyCycle(0)
    pwm.stop()
    GPIO.cleanup()
