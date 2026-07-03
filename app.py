import os
import requests
import telebot
from threading import Thread
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Бот работает на мощном RapidAPI!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Твой ключ со скриншота
RAPID_API_KEY = "7b12feec3fmsh0341f118809e1a0p1e0e7jsn8ff1254bfba9"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Бот успешно обновлен на стабильный RapidAPI 🚀\nОтправляй ссылку на TikTok!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()
    if "tiktok.com" not in url:
        bot.reply_to(message, "Это не похоже на ссылку TikTok 🤖")
        return

    status_msg = bot.reply_to(message, "Скачиваю видео без водяного знака... ⏳")
    try:
        # Раскрываем короткие ссылки, если это vt.tiktok или vm.tiktok
        headers_redirect = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        if "vt.tiktok.com" in url or "vm.tiktok.com" in url:
            res = requests.get(url, headers=headers_redirect, allow_redirects=True, timeout=15)
            clean_url = res.url.split('?')[0]
        else:
            clean_url = url.split('?')[0]

        # Запрос к твоему API со скриншота
        api_url = "https://tiktok-video-no-watermark2.p.rapidapi.com/"
        querystring = {"url": clean_url, "hd": "1"}
        headers = {
            "X-RapidAPI-Key": RAPID_API_KEY,
            "X-RapidAPI-Host": "tiktok-video-no-watermark2.p.rapidapi.com"
        }
        
        response = requests.get(api_url, headers=headers, params=querystring, timeout=20).json()

        if response.get('code') == 0 and 'data' in response:
            # Пробуем взять HD, если нет — обычное без водянки
            video_url = response['data'].get('hdplay') or response['data'].get('play')
            
            if video_url:
                video_data = requests.get(video_url, timeout=30).content
                filename = f"video_{message.chat.id}.mp4"
                
                with open(filename, 'wb') as f:
                    f.write(video_data)

                with open(filename, 'rb') as video:
                    bot.send_video(message.chat.id, video, reply_to_message_id=message.message_id)

                bot.delete_message(message.chat.id, status_msg.message_id)
                os.remove(filename)
                return

        bot.edit_message_text("Не удалось скачать. Проверь, что видео открыто для всех.", message.chat.id, status_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text("Произошла ошибка при скачивании файла. Попробуй еще раз.", message.chat.id, status_msg.message_id)

if __name__ == '__main__':
    Thread(target=run_web).start()
    bot.infinity_polling()
