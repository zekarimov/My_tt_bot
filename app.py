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
    text = (
        "🤖 **Я — твой персональный загрузчик контента из TikTok!**\n\n"
        "⚡ **Что я умею:**\n"
        "• Скачивать любые видео из TikTok по ссылке.\n"
        "• Удалять водяные знаки.\n"
        "• Работать с мобильными ссылками (`vt.tiktok.com`).\n\n"
        "Отправляй ссылку, и я пришлю видео!"
    )
    bot.reply_to(message, text, parse_mode='Markdown')

def get_real_url(url):
    # Распаковываем короткие мобильные ссылки
    if "vt.tiktok.com" in url or "vm.tiktok.com" in url:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            res = requests.get(url, headers=headers, allow_redirects=True, timeout=15)
            return res.url.split('?')[0]
        except:
            return url.split('?')[0]
    return url.split('?')[0]

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()
    if "tiktok.com" not in url:
        bot.reply_to(message, "Это не похоже на ссылку TikTok 🤖")
        return

    status_msg = bot.reply_to(message, "Разбираю ссылку... ⏳")
    
    try:
        real_url = get_real_url(url)
        bot.edit_message_text("Связываюсь с сервером загрузки... ⏳", message.chat.id, status_msg.message_id)

        api_url = "https://tiktok-video-no-watermark2.p.rapidapi.com/"
        querystring = {"url": real_url, "hd": "1"}
        headers = {
            "X-RapidAPI-Key": RAPID_API_KEY,
            "X-RapidAPI-Host": "tiktok-video-no-watermark2.p.rapidapi.com"
        }
        
        response = requests.get(api_url, headers=headers, params=querystring, timeout=20).json()

        if response.get('code') == 0 and 'data' in response:
            video_url = response['data'].get('hdplay') or response['data'].get('play')
            
            if video_url:
                bot.edit_message_text("Скачиваю видео без водяного знака... ⏳", message.chat.id, status_msg.message_id)
                # Скачиваем видео в память бота
                vid_req = requests.get(video_url, timeout=30)
                
                if vid_req.status_code == 200:
                    bot.edit_message_text("Отправляю видео в чат... 🚀", message.chat.id, status_msg.message_id)
                    # Отправляем скачанный файл в Телеграм
                    bot.send_video(message.chat.id, vid_req.content, reply_to_message_id=message.message_id)
                    bot.delete_message(message.chat.id, status_msg.message_id)
                    return
        
        bot.edit_message_text("Не удалось скачать. Возможно, видео приватное или API не ответило.", message.chat.id, status_msg.message_id)
            
    except Exception as e:
        # Теперь бот пришлет точную причину ошибки прямо в чат!
        bot.edit_message_text(f"Произошла ошибка: {str(e)[:100]}", message.chat.id, status_msg.message_id)

def run_bot():
    while True:
        try:
            bot.delete_webhook(drop_pending_updates=True)
            time.sleep(1)
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception:
            time.sleep(5)

if __name__ == '__main__':
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
