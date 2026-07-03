import os
import requests
import telebot

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Бот успешно запущен на Render 🚀\nОтправь мне ссылку на TikTok!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()
    if "tiktok.com" not in url:
        bot.reply_to(message, "Это не похоже на ссылку TikTok 🤖")
        return

    status_msg = bot.reply_to(message, "Скачиваю видео напрямую... ⏳")
    try:
        clean_url = url.split('?')[0]
        api_url = f"https://api.tikwm.com/api/?url={clean_url}"
        response = requests.get(api_url, timeout=20).json()

        if response.get('code') == 0 and response.get('data'):
            video_url = response['data']['play']
            video_data = requests.get(video_url, timeout=20).content
            filename = "tiktok_video.mp4"
            
            with open(filename, 'wb') as f:
                f.write(video_data)

            with open(filename, 'rb') as video:
                bot.send_video(message.chat.id, video, reply_to_message_id=message.message_id)

            bot.delete_message(message.chat.id, status_msg.message_id)
            os.remove(filename)
        else:
            bot.edit_message_text("Не удалось скачать видео. Возможно, оно приватное.", message.chat.id, status_msg.message_id)
    except Exception as e:
        bot.edit_message_text("Ошибка обработки. Попробуй ещё раз.", message.chat.id, status_msg.message_id)

if __name__ == '__main__':
    bot.infinity_polling()
