import os
import time
from threading import Thread
import requests
import telebot
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Бот работает на мощном RapidAPI!"

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Твой ключ
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
        clean_url = url.split('?')[0]

        api_url = "https://tiktok-video-no-watermark2.p.rapidapi.com/"
        querystring = {"url": clean_url, "hd": "1"}
        headers = {
            "X-RapidAPI-Key": RAPID_API_KEY,
            "X-RapidAPI-Host": "tiktok-video-no-watermark2.p.rapidapi.com"
        }
        
        response = requests.get(api_url, headers=headers, params=querystring, timeout=20).json()

        if response.get('code') == 0 and 'data' in response:
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

def run_bot():
    while True:
        try:
            # Сбрасываем старые сессии перед каждым запуском
            bot.delete_webhook(drop_pending_updates=True)
            time.sleep(1)
            # Запуск стандартного пуллинга
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            # Если Телеграм ругается, ждем 5 секунд и пробуем снова
            time.sleep(5)

if __name__ == '__main__':
    # Запускаем бота в фоновом потоке через безопасную функцию
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # Flask сервер держит порт 10000 для Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
