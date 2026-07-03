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

    # 3. Затем запускаем Flask веб-сервер на главном потоке (чтобы Render сразу видел порт 10000)
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
