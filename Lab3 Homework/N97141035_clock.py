from time import sleep, localtime
from tm1637 import TM1637

# 注意：tm1637 函式庫內部使用 BCM 腳位編號 (GPIO.setmode(GPIO.BCM))，
# 跟 LED/蜂鳴器程式用的 BOARD 編號不一樣！
CLK = 24   # BCM 編號 = BOARD 第 18 腳 (已與 DIO 對調測試)
DIO = 23   # BCM 編號 = BOARD 第 16 腳 (已與 CLK 對調測試)


class Clock:
    def __init__(self, tm_instance):
        self.tm = tm_instance
        self.show_colon = False

    def run(self):
        while True:
            t = localtime()
            self.show_colon = not self.show_colon
            self.tm.numbers(t.tm_hour, t.tm_min, self.show_colon)
            sleep(1)


if __name__ == '__main__':
    tm = TM1637(CLK, DIO)
    tm.brightness(1)
    clock = Clock(tm)
    try:
        clock.run()
    except KeyboardInterrupt:
        pass
