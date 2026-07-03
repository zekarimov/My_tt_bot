import os
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
        # Просто очищаем хвост ссылки от лишних параметров отслеживания
        clean_url = url.split('?')[0]

        api_url = "https://tiktok-video-no-watermark2.p.rapidapi.com/"
        querystring = {"url": clean_url, "hd": "1"}
        headers = {
            "X-RapidAPI-Key": RAPID_API_KEY,
            "X-RapidAPI-Host": "tiktok-video-no-watermark2.p.rapidapi.com"
        }
        
        # Отправляем ссылку напрямую в RapidAPI
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

if __name__ == '__main__':
    # 1. Принудительно сбрасываем старые зависшие сообщения в самом Telegram
    try:
        bot.delete_webhook(drop_pending_updates=True)
    except:
        pass

    # 2. Сначала запускаем бесконечный опрос Telegram бота в отдельном потоке
    bot_thread = Thread(target=bot.infinity_polling)
    bot_thread.daemon = True
    bot_thread.start()

    # 3. Затем запускаем Flask веб-сервер на главном потоке
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
