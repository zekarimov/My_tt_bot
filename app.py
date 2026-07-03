import os
import requests
import telebot
from threading import Thread
from flask import Flask

app_web = Flask('')

@app_web.route('/')
def home():
    return "Бот работает стабильно!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host='0.0.0.0', port=port)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Бот успешно запущен на Render 🚀\nОтправь мне любую ссылку на TikTok (даже vt.tiktok.com)!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()
    if "tiktok.com" not in url:
        bot.reply_to(message, "Это не похоже на ссылку TikTok 🤖")
        return

    status_msg = bot.reply_to(message, "Обрабатываю ссылку и скачиваю видео... ⏳")
    try:
        # Если ссылка короткая (мобильная), получаем полный её адрес
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        if "vt.tiktok.com" in url or "vm.tiktok.com" in url:
            res = requests.get(url, headers=headers, allow_redirects=True, timeout=15)
            clean_url = res.url.split('?')[0]
        else:
            clean_url = url.split('?')[0]

        # Запрос к API скачивания
        api_url = f"https://api.tikwm.com/api/?url={clean_url}"
        response = requests.get(api_url, headers=headers, timeout=20).json()

        if response.get('code') == 0 and response.get('data'):
            video_url = response['data']['play']
            video_data = requests.get(video_url, timeout=20).content
            filename = f"video_{message.chat.id}.mp4"
            
            with open(filename, 'wb') as f:
                f.write(video_data)

            with open(filename, 'rb') as video:
                bot.send_video(message.chat.id, video, reply_to_message_id=message.message_id)

            bot.delete_message(message.chat.id, status_msg.message_id)
            os.remove(filename)
        else:
            error_msg = response.get('msg', 'Видео приватное или удалено.')
            bot.edit_message_text(f"API не смог скачать видео. Причина: {error_msg}", message.chat.id, status_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"Произошла ошибка при обработке файла. Попробуй другую ссылку.", message.chat.id, status_msg.message_id)

if __name__ == '__main__':
    Thread(target=run_web).start()
    bot.infinity_polling()


