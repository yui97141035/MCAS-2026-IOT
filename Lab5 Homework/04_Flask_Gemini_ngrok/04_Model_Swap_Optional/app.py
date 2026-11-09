import os
from functools import wraps

from dotenv import load_dotenv
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from openai import OpenAI


# =========================
# Environment Variables
# =========================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

if not GROQ_API_KEY:
    raise RuntimeError(
        "找不到 GROQ_API_KEY，請先建立 .env 並填入 API Key。"
    )

if not SECRET_KEY or SECRET_KEY == "CHANGE_ME":
    raise RuntimeError(
        "請在 .env 設定安全的 SECRET_KEY。"
    )


# =========================
# Flask
# =========================

app = Flask(__name__)
app.secret_key = SECRET_KEY


# Lab 用簡化帳號
# 正式系統不應以明文保存密碼
USERS = {
    "admin": "1234",
}


# =========================
# Groq (OpenAI-compatible API)
# =========================

groq_client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

SYSTEM_PROMPT = {
    "role": "system",
    "content": "你是 Lab6 進階題的聊天助理，請用繁體中文簡潔回覆。",
}


def ask_groq(history):
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[SYSTEM_PROMPT] + history,
    )

    reply = (response.choices[0].message.content or "").strip()

    if not reply:
        reply = "Groq 沒有回傳文字內容。"

    return reply


# =========================
# Login Required
# =========================

def login_required(view):

    @wraps(view)
    def wrapped(*args, **kwargs):

        if "user" not in session:

            if request.path.startswith("/api/"):
                return jsonify({
                    "error": "請先登入"
                }), 401

            return redirect(url_for("login"))

        return view(*args, **kwargs)

    return wrapped


# =========================
# Login
# =========================

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username in USERS and USERS[username] == password:
            session.clear()
            session["user"] = username
            return redirect(url_for("chat_room"))

        return render_template("login.html", msg="帳號或密碼錯誤")

    if "user" in session:
        return redirect(url_for("chat_room"))

    return render_template("login.html")


# =========================
# Chat Page
# =========================

@app.get("/chat")
@login_required
def chat_room():
    return render_template("chat.html", username=session["user"])


# =========================
# Groq Chat API
# =========================

@app.post("/api/chat")
@login_required
def api_chat():

    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "訊息不可為空"}), 400

    if len(message) > 2000:
        return jsonify({"error": "訊息過長"}), 400

    try:
        history = session.get("chat_history", [])
        history.append({"role": "user", "content": message})

        reply = ask_groq(history)

        history.append({"role": "assistant", "content": reply})

        # 只保留最近 20 則，避免 session cookie 過大
        session["chat_history"] = history[-20:]

        return jsonify({"reply": reply})

    except Exception as error:
        print("[Groq API Error]", error)
        return jsonify({
            "error": "Groq API 呼叫失敗，請檢查 API Key、網路或模型設定。"
        }), 502


# =========================
# Reset Conversation
# =========================

@app.post("/api/reset")
@login_required
def reset_chat():
    session.pop("chat_history", None)
    return jsonify({"ok": True})


# =========================
# Logout
# =========================

@app.post("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))


# =========================
# Run Server
# =========================

if __name__ == "__main__":
    print("=== Lab6 進階題：Groq 版 Flask Server ===")
    print("Listening on http://0.0.0.0:3001")
    app.run(host="0.0.0.0", port=3001, debug=False)
