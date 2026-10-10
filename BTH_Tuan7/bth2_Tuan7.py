import RPi.GPIO as GPIO
import time

# Cấu hình các chân kết nối LCD và nút bấm
LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
BT_1 = 21
BT_2 = 26
PWM_PIN = 24
DIR_PIN = 25

LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(PWM_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

pwm = GPIO.PWM(PWM_PIN, 1000)
pwm.start(0)

speed = 0


def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    for byte in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
        lcd_byte(byte, LCD_CMD)


def lcd_clear():
    lcd_byte(0x01, LCD_CMD)


def lcd_byte(bits, mode):
    GPIO.output(LCD_PINS['RS'], mode)
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num + 4}'], bits & (1 << (4 + bit_num)) != 0)
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num + 4}'], bits & (1 << bit_num) != 0)
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)


def lcd_display_string(message, line):
    lcd_byte(LCD_LINE_1 if line == 1 else LCD_LINE_2, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)


def motor_control(speed, direction=0):
    GPIO.output(DIR_PIN, direction)
    pwm.ChangeDutyCycle(speed)


def main():
    global speed
    lcd_init()
    motor_control(0)

    last_increase_time = time.time()

    while True:
        # Nếu nhấn nút 2: Ngay lập tức dừng lại hẳn
        if GPIO.input(BT_2) == GPIO.LOW:
            speed = 0
            motor_control(0)
            lcd_display_string("Trang thai: Dung", 1)
            lcd_display_string("Toc do: 0%      ", 2)
            time.sleep(0.2)
            continue

        # Nếu nhấn và giữ nút 1: Tăng 10% tốc độ mỗi giây đến tối đa 100%
        if GPIO.input(BT_1) == GPIO.LOW:
            current_time = time.time()
            if current_time - last_increase_time >= 1.0:
                if speed < 100:
                    speed += 10
                    if speed > 100:
                        speed = 100
                last_increase_time = current_time

            motor_control(speed)
            lcd_display_string("Chieu: Quay Thuan", 1)
            lcd_display_string(f"Toc do: {speed}%    ", 2)
        else:
            last_increase_time = time.time()

        time.sleep(0.05)  # Delay ngắn để bắt phản hồi nút bấm khẩn cấp BT_2 ngay lập tức


try:
    main()
except KeyboardInterrupt:
    pwm.stop()
    lcd_clear()
    GPIO.cleanup()