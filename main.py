#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import telebot
import requests
import random
import time
import os
import threading
from flask import Flask

# ================= TOKENLAR =================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode="HTML")

STICKERS = [
    "CAACAgIAAxkBAAIBjGbC_V8NRhS2ObgABqYmRf38GILucgAC_hcAAu9pOUqS7VEEVhLQQzQE",
    "CAACAgIAAxkBAAIBjWbC_WBri-ocw3D_nODoxYHt8QzTAAKvGwACgmcAAUoI1hTx2ZR8vTQE",
]

# ================= AI FUNKSIYA =================
def get_ai_response(text):
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://telegram.org",
            "X-Title": "Erkinov AI Bot"
        }

        payload = {
            "model": "meta-llama/llama-3.1-8b-instruct",
            "messages": [
                {"role": "system", "content": "O'zbek tilida aniq, tartiblangan va chiroyli javob ber."},
                {"role": "user", "content": text}
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }

        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=20
        )

        if r.status_code != 200:
            return "AI hozir javob bera olmadi."

        return r.json()["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print("AI ERROR:", e)
        return "Texnik xato yuz berdi."

# ================= TELEGRAM HANDLER =================
@bot.message_handler(commands=['start'])
def start(message):
    try:
        bot.send_sticker(message.chat.id, random.choice(STICKERS))
    except:
        pass
    bot.send_message(
        message.chat.id,
        "<b>👋 Salom!</b>\n\nSavolingizni yozing, men javob beraman."
    )

@bot.message_handler(func=lambda m: True)
def handle(m):
    if not m.text:
        return
    text = m.text.lower()
    if any(x in text for x in ["kim yaratdi", "yaratuvchi", "seni kim", "kim qildi"]):
        bot.send_message(m.chat.id, "🤖 Bu bot Mehruzbek Erkinov tomonidan yaratilgan.")
        return

    bot.send_chat_action(m.chat.id, "typing")
    wait = bot.send_message(m.chat.id, "⏳ Javob tayyorlanmoqda...")

    ai = get_ai_response(m.text)

    try:
        bot.delete_message(m.chat.id, wait.message_id)
    except:
        pass

    try:
        bot.send_sticker(m.chat.id, random.choice(STICKERS))
    except:
        pass

    final_answer = f"""
<b>🧠 Javob:</b>

{ai}

━━━━━━━━━━━━━━
🤖 <b>Erkinov AI</b> | <a href="https://t.me/ErkinovAIBot">@ErkinovAIBot</a>
"""
    bot.send_message(m.chat.id, final_answer)

# ================= THREAD BOSHQARISH =================
def run_bot():
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

# ================= FLASK APP =================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot ishlayapti! ✅"

# Botni alohida threadda ishga tushiramiz
threading.Thread(target=run_bot).start()

# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
