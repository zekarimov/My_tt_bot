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
    capabilities_text = (
        "🤖 **Я — твой персональный загрузчик контента из TikTok!**\n\n"
        "⚡ **Что я умею:**\n"
        "• Скачивать любые видео из TikTok по ссылке.\n"
        "• Полностью удалять водяные знаки (watermarks) с видео.\n"
        "• Сохранять ролики в максимально доступном HD-качестве.\n"
        "• Работать как с полными, так и с короткими мобильными ссылками (`vt.tiktok.com`).\n\n"
        "🚀 **Как мной пользоваться:**\n"
        "Просто скопируй ссылку на понравившийся ролик в TikTok и отправь её мне в чат. Я тут же пришлю тебе готовый видеофайл, который можно сохранить на устройство или переслать друзьям!"
    )
    bot.reply_to(message, capabilities_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()
    if "tiktok.com" not in url:
        bot.reply_to(message, "Это не похоже на ссылку TikTok 🤖")
        return

    status_msg = bot.reply_to(message, "Скачиваю видео без водяного знака... ⏳")
    try:
        # Корректно разворачиваем мобильные ссылки vt.tiktok.com и vm.tiktok.com
        if "vt.tiktok.com" in url or "vm.tiktok.com" in url:
            headers_redirect = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
            }
            res = requests.get(url, headers=headers_redirect, allow_redirects=True, timeout=15)
            clean_url = res.url.split('?')[0]
        else:
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
            bot.delete_webhook(drop_pending_updates=True)
            time.sleep(1)
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            time.sleep(5)

if __name__ == '__main__':
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
