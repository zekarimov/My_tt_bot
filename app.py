import os
import time
from threading import Thread
import requests
import telebot
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Бот работает!"

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
RAPID_API_KEY = "7b12feec3fmsh0341f118809e1a0p1e0e7jsn8ff1254bfba9"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Бот готов! Присылай ссылку на TikTok.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()
    if "tiktok.com" not in url:
        return

    status_msg = bot.reply_to(message, "Загружаю... ⏳")
    try:
        api_url = "https://tiktok-video-no-watermark2.p.rapidapi.com/"
        querystring = {"url": url, "hd": "1"}
        headers = {
            "X-RapidAPI-Key": RAPID_API_KEY,
            "X-RapidAPI-Host": "tiktok-video-no-watermark2.p.rapidapi.com"
        }
        response = requests.get(api_url, headers=headers, params=querystring, timeout=20).json()
        
        if response.get('code') == 0:
            video_url = response['data']['hdplay']
            bot.send_video(message.chat.id, video_url)
            bot.delete_message(message.chat.id, status_msg.message_id)
        else:
            bot.edit_message_text("Ошибка API: " + str(response), message.chat.id, status_msg.message_id)
    except Exception as e:
        bot.edit_message_text("Ошибка: " + str(e), message.chat.id, status_msg.message_id)

def run_bot():
    while True:
        try:
            bot.delete_webhook(drop_pending_updates=True)
            bot.polling(none_stop=True)
        except:
            time.sleep(5)

if __name__ == '__main__':
    Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
