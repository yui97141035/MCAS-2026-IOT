import RPi.GPIO as GPIO
import time

LED_PIN = 11      # LED 訊號腳位 (BOARD 編號)
BUZZER_PIN = 12   # 蜂鳴器訊號腳位 (BOARD 編號)
FREQ = 523        # 蜂鳴器音調 (Hz)

UNIT = 0.2                  # 一個「短音(dit)」的時間單位，可自行調整快慢
DOT = UNIT                  # 短音
DASH = UNIT * 3              # 長音
GAP_SYMBOL = UNIT            # 同一字母內，訊號之間的間隔
GAP_LETTER = UNIT * 3        # 字母與字母之間的間隔

GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
buzzer = GPIO.PWM(BUZZER_PIN, FREQ)


def signal_on():
    GPIO.output(LED_PIN, True)
    buzzer.start(50)


def signal_off():
    GPIO.output(LED_PIN, False)
    buzzer.stop()


def dit():
    signal_on()
    time.sleep(DOT)
    signal_off()
    time.sleep(GAP_SYMBOL)


def dah():
    signal_on()
    time.sleep(DASH)
    signal_off()
    time.sleep(GAP_SYMBOL)


def letter_S():
    dit(); dit(); dit()


def letter_O():
    dah(); dah(); dah()


try:
    while True:
        letter_S()
        time.sleep(GAP_LETTER)
        letter_O()
        time.sleep(GAP_LETTER)
        letter_S()
        time.sleep(GAP_LETTER * 2)   # 一輪 SOS 結束，多停一下再重複
except KeyboardInterrupt:
    pass
finally:
    buzzer.stop()
    del buzzer
    GPIO.cleanup()
