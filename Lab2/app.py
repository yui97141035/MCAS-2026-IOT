from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

images = [
    "images/pic1.jpg",
    "images/pic2.jpg",
    "images/pic3.jpg"
]

current_index = 0  # 全域索引

@app.route("/")
def index():
    global current_index
    img = images[current_index]
    return render_template("index.html", image=img, idx=current_index, total=len(images))

@app.route("/next")
def next_img():
    global current_index
    # 修正 bug：原本沒有邊界檢查，index 超出 images 範圍時
    # images[current_index] 會丟出 IndexError，導致網站顯示 500 錯誤。
    # 改用取餘數(modulo)讓索引在 0 ~ len(images)-1 之間循環，
    # 點到最後一張後再按「下一張」會自然繞回第一張。
    current_index = (current_index + 1) % len(images)
    return redirect(url_for("index"))

@app.route("/prev")
def prev_img():
    global current_index
    current_index = (current_index - 1) % len(images)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
