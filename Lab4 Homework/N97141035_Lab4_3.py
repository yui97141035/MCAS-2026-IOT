import serial
import time
import RPi.GPIO as GPIO

# 設定 UART 連接埠與參數 (預設使用 /dev/serial0)
ser = serial.Serial(
    port='/dev/serial0',    # 對應 GPIO14 (TX, 第8腳) 和 GPIO15 (RX, 第10腳)
    baudrate=9600,          # 傳輸速率
    timeout=1               # 讀取逾時設定 (秒)
)

LED_PIN = 11                # LED 訊號腳位 (BOARD 編號)

UNIT = 0.2                  # 一個「短音(dit)」的時間單位
DOT = UNIT                  # 短
DASH = UNIT * 3             # 長
GAP_SYMBOL = UNIT           # 同一字元內，訊號之間的間隔
GAP_LETTER = UNIT * 3       # 字元與字元之間的間隔
GAP_WORD = UNIT * 7         # 空白 (單字之間) 的間隔

# 摩斯密碼表：英文字母 + 數字
MORSE = {
    'A': '.-',    'B': '-...',  'C': '-.-.',  'D': '-..',   'E': '.',
    'F': '..-.',  'G': '--.',   'H': '....',  'I': '..',    'J': '.---',
    'K': '-.-',   'L': '.-..',  'M': '--',    'N': '-.',    'O': '---',
    'P': '.--.',  'Q': '--.-',  'R': '.-.',   'S': '...',   'T': '-',
    'U': '..-',   'V': '...-',  'W': '.--',   'X': '-..-',  'Y': '-.--',
    'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
}

GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT, initial=False)


# 傳送資料
def send_data(data):
    if ser.is_open:
        ser.write((data + '\n').encode('utf-8'))
        print(f"已傳送：{data}")


# 接收資料
def receive_data():
    if ser.is_open:
        incoming = ser.readline().decode('utf-8', errors='replace').strip()
        if incoming:
            print(f"收到資料：{incoming}")
        return incoming


# LED 閃一次 (duration 為亮的時間)
def blink(duration):
    GPIO.output(LED_PIN, True)
    time.sleep(duration)
    GPIO.output(LED_PIN, False)
    time.sleep(GAP_SYMBOL)


# 將收到的字串以摩斯密碼顯示在 LED 上
def show_on_led(text):
    codes = []
    for ch in text.upper():
        if ch == ' ':
            codes.append('/')
            time.sleep(GAP_WORD)
            continue
        code = MORSE.get(ch)
        if code is None:          # 不支援的字元就跳過
            continue
        codes.append(code)
        for symbol in code:
            blink(DOT if symbol == '.' else DASH)
        time.sleep(GAP_LETTER)
    print(f"LED 摩斯密碼：{' '.join(codes)}")


# 主程式
try:
    ser.reset_input_buffer()
    while True:
        data = input("請輸入要傳送的數字或字元 (Ctrl+C 結束)：").strip()
        if not data:
            continue
        send_data(data)
        time.sleep(0.1)
        incoming = receive_data()
        if incoming:
            show_on_led(incoming)
        else:
            print("沒有收到資料，請檢查 TX(第8腳) 與 RX(第10腳) 是否相接")

except (KeyboardInterrupt, EOFError):
    print("\n程式中斷")

finally:
    GPIO.cleanup()
    if ser.is_open:
        ser.close()
        print("串列埠已關閉")
