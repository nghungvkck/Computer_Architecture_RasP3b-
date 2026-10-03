import RPi.GPIO as GPIO
import time

LCD_PINS = {'RS': 23,     # chân RS là chân chọn thanh ghi, logic 0 là chọn thanh ghi lệnh, logic 1 là chọn thanh ghi dữ liệu
            'E': 27,      # chân E là chân cho phép, khi chân này ở mức logic 1 thì LCD sẽ nhận dữ liệu, khi ở mức logic 0 thì LCD sẽ không nhận dữ liệu
            'D4': 18,     # chân D4 là chân dữ liệu 4
            'D5': 17,     # chân D5 là chân dữ liệu 5
            'D6': 14,     # chân D6 là chân dữ liệu 6
            'D7': 3,      # chân D7 là chân dữ liệu 7
            'BL': 2}      # chân BL là chân đèn nền
LCD_WIDTH = 16            # Số ký tự trên mỗi dòng của LCD
LCD_CHR = True            # Chế độ ký tự (True) hoặc lệnh (False)
LCD_CMD = False           # Chế độ lệnh (False) hoặc ký tự (True)

LCD_LINE_1 = 0x80         # Địa chỉ của dòng 1 trên LCD
LCD_LINE_2 = 0xC0         # Địa chỉ của dòng 2 trên LCD

E_PULSE = 0.0005          # Thời gian xung E (tính bằng giây)
E_DELAY = 0.0005          # Thời gian trễ giữa các xung E (tính bằng giây)

def lcd_init(): #  hảm khởi tạo GPIO
    GPIO.setmode(GPIO.BCM)   # Chế độ đánh số chân GPIO theo BCM
    GPIO.setwarnings(False)  # Tắt cảnh báo GPIO

    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)   # Thiết lập các chân LCD là đầu ra
    
    lcd_byte(0x33, LCD_CMD)  # thiết lập chế độ 4 bit/8_bit
    lcd_byte(0x32, LCD_CMD)  # chuyển sang chế độ 4 bit
    lcd_byte(0x28, LCD_CMD)  # cấu hình 4-bit. 2 dòng, 5x7 điểm
    lcd_byte(0x0C, LCD_CMD)  # bật hiển thị, tắt con trỏ
    lcd_byte(0x06, LCD_CMD)  # thiết lập con trỏ tự tăng sang phải sau mỗi ký tự được viết
    lcd_byte(0x01, LCD_CMD)  # xóa màn hình
    time.sleep(E_DELAY)      # đợi LCD xử lý lệnh xóa màn hình

def lcd_clear():   # hàm xóa màn hình LCD
    lcd_byte(0x01, LCD_CMD)
    time.sleep(E_DELAY)  # đợi LCD xử lý lệnh xóa màn hình

def lcd_byte(bits, mode):   # hàm gửi dữ liệu hoặc lệnh đến LCD
    GPIO.output(LCD_PINS['RS'], mode)  
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num + 4}'], 
                    bits & (1 << (4 + bit_num)) != 0
                    ) # Gửi 4 bit cao của dữ liệu hoặc lệnh đến LCD
        
    time.sleep(E_DELAY) 
    GPIO.output(LCD_PINS['E'], True) 
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False) 
    time.sleep(E_DELAY)
    
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num + 4}'], 
                    bits & (1 << (4 + bit_num)) != 0
                    ) # gửi 4 bit thấp của dữ liệu hoặc lệnh đến LCD
        
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)

# hàm hiển thị chuỗi ký tự trên LCD, tham số message là chuỗi ký tự cần hiển thị, line là dòng hiển thị (1 hoặc 2)
def lcd_display_string(message, line):  
    if line == 1:
        lcd_byte(LCD_LINE_1, LCD_CMD)  # gửi lệnh chọn dòng 1
    elif line == 2:
        lcd_byte(LCD_LINE_2, LCD_CMD)  # gửi lệnh chọn dòng 2
    for char in message:
        lcd_byte(ord(char), LCD_CHR)  # gửi ký tự đến LCD

# hàm main
def main():
    lcd_init()
    lcd_clear()
    GPIO.output(LCD_PINS['BL'], True) # Bật đèn nền LCD
    lcd_display_string("Hello-World!", 1)  #H Hiển thị màn hình
    
    while True:
        time.sleep(1) 

try:
    main()
except KeyboardInterrupt:
    lcd_clear()
    GPIO.cleanup()