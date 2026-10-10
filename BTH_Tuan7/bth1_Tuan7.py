import RPi.GPIO as GPIO
import time

# Cấu hình các chân kết nối LCD và linh kiện
LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
BT_1 = 21
PWM_PIN = 24
DIR_PIN = 25
LED_PIN = 16  # Chân GPIO kết nối LED cảnh báo (tự chọn chân 16)

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
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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
    GPIO.output(LED_PIN, False)

    while True:
        # Nếu nhấn và giữ nút BT_1
        if GPIO.input(BT_1) == GPIO.LOW:
            if speed < 100:
                speed += 10
                if speed > 100:
                    speed = 100

            motor_control(speed)

            # Kiểm tra tốc độ > 80% để bật LED cảnh báo
            if speed > 80:
                GPIO.output(LED_PIN, True)
            else:
                GPIO.output(LED_PIN, False)

            lcd_display_string("Chieu: Quay Thuan", 1)
            lcd_display_string(f"Toc do: {speed}%    ", 2)
            time.sleep(1)  # Tăng 10% mỗi giây
        else:
            # Thả nút BT_1: Động cơ dừng hẳn
            speed = 0
            motor_control(0)
            GPIO.output(LED_PIN, False)
            lcd_display_string("Chieu: Dung    ", 1)
            lcd_display_string("Toc do: 0%      ", 2)
            time.sleep(0.1)


try:
    main()
except KeyboardInterrupt:
    pwm.stop()
    lcd_clear()
    GPIO.cleanup()