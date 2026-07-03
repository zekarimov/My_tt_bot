        # Замени старую проверку на эту:
        response = requests.get(api_url, headers=headers, params=querystring, timeout=20).json()

        # Если код не 0, бот напишет реальную причину в чат
        if response.get('code') != 0:
            msg_text = f"API ОШИБКА: {response.get('msg', 'Неизвестная ошибка')}"
            bot.edit_message_text(msg_text, message.chat.id, status_msg.message_id)
            return
