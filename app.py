import os
import requests
import telebot
from threading import Thread
from flask import Flask

app_web = Flask('')

@app_web.route('/')
def home():
    return "Бот работает на новом API!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host='0.0.0.0', port=port)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Бот обновлен и готов к работе 🚀\nОтправь мне ссылку на TikTok!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()
    if "tiktok.com" not in url:
        bot.reply_to(message, "Это не похоже на ссылку TikTok 🤖")
        return

    status_msg = bot.reply_to(message, "Скачиваю видео через резервный канал... ⏳")
    try:
        # Используем стабильный TikFast API
        api_url = f"https://api.tikfast.net/api/v1/download?url={url}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        
        response = requests.get(api_url, headers=headers, timeout=20).json()

        # Проверяем успешный ответ от TikFast
        if response.get('status') == True and 'links' in response:
            # Берем ссылку на видео без водяного знака
            video_url = response['links'].get('no_watermark_hd') or response['links'].get('no_watermark')
            
            if video_url:
                video_data = requests.get(video_url, timeout=25).content
                filename = f"video_{message.chat.id}.mp4"
                
                with open(filename, 'wb') as f:
                    f.write(video_data)

                with open(filename, 'rb') as video:
                    bot.send_video(message.chat.id, video, reply_to_message_id=message.message_id)

                bot.delete_message(message.chat.id, status_msg.message_id)
                os.remove(filename)
                return
                
        bot.edit_message_text("Не удалось получить видео. Возможно, ссылка устарела или видео приватное.", message.chat.id, status_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text("Ошибка сети. Попробуй отправить ссылку еще раз через минуту.", message.chat.id, status_msg.message_id)

if __name__ == '__main__':
    Thread(target=run_web).start()
    bot.infinity_polling()
