import RPi.GPIO as GPIO
import time

# 設定使用 BCM 編號系統
GPIO.setmode(GPIO.BCM)

# 超聲波模組的 TRIG_y 與 ECHO_r 引腳設定
TRIG_y = 23  # GPIO 23 (實體第16腳)
ECHO_r = 24  # GPIO 24 (實體第18腳)

# 警告距離 (公分)
WARN_DISTANCE = 20


# 設定引腳輸出入模式
GPIO.setup(TRIG_y, GPIO.OUT)
GPIO.setup(ECHO_r, GPIO.IN)


def measure_distance():
    # 確保發射端是關閉的，並稍作延遲讓感測器穩定
    GPIO.output(TRIG_y, False)
    time.sleep(0.5)

    # 發送 10微秒 的高電位脈衝來觸發超聲波
    GPIO.output(TRIG_y, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_y, False)

    # 等待 ECHO_r 高電位 (1)，並記錄起始時間 (超過 0.1 秒視為量測失敗)
    pulse_start = time.time()
    timeout = pulse_start + 0.1
    while GPIO.input(ECHO_r) == 0:
        pulse_start = time.time()
        if pulse_start > timeout:
            return None

    # 等待 ECHO_r 變回低電位 (0)，並記錄結束時間
    pulse_end = time.time()
    timeout = pulse_end + 0.1
    while GPIO.input(ECHO_r) == 1:
        pulse_end = time.time()
        if pulse_end > timeout:
            return None

    # 計算脈衝持續時間，並根據音速轉換為距離 (公分)
    # 距離 = (時間 * 聲速 34300 cm/s) / 2
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance


try:
    while True:
        distance = measure_distance()
        if distance is None:
            print("量測失敗，請檢查接線")
            continue

        print(f"目前距離： {distance} cm")
        # 模擬倒車雷達：小於 20 cm 就發出警告
        if distance < WARN_DISTANCE:
            print("注意！！！")
        else:
            print("沒事")

except KeyboardInterrupt:
    print("程式中斷")

finally:
    GPIO.cleanup()
