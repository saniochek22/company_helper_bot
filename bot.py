import telebot
import time
from db import (
    create_table_if_not_exists,
    get_user_role,
    get_user_department,
    save_user_info,
    user_exists,
    get_decrypted_bot_token,
    create_bot_config_table,
)
from ai import ask_ai
from dotenv import load_dotenv
import os

load_dotenv()
create_bot_config_table()

# 🔁 Ожидаем появления токена в базе
token = None
while token is None:
    try:
        token = get_decrypted_bot_token()
    except Exception as e:
        print("⏳ Токен не найден в базе. Ожидаю 5 секунд...")
        time.sleep(5)

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def handle_start(message):
    telegram_id = message.from_user.id
    username = message.from_user.username or ""

    if user_exists(telegram_id):
        bot.send_message(
            message.chat.id,
            f"👋 Добро пожаловать обратно, @{username}! Просто задай свой вопрос, и я постараюсь помочь.\n"
            "Если вы видите это сообщение, но вам пишут 'роль не задана' — обратитесь к администратору."
        )
    else:
        save_user_info(telegram_id, username)
        bot.send_message(
            message.chat.id,
            f"✅ Привет, @{username or 'новый пользователь'}! Ты добавлен в базу. Просто задай свой вопрос, и я постараюсь помочь.\n"
            "Если вы видите это сообщение, но вам пишут 'роль не задана' — обратитесь к администратору."
        )


@bot.message_handler(func=lambda msg: True)
def handle_user_question(message):
    user_id = message.from_user.id
    role = get_user_role(user_id)
    department = get_user_department(user_id)

    if not role or not department:
        bot.reply_to(message, "Ваши роль и отдел ещё не заданы. Обратитесь к администратору.")
        return

    question = message.text
    bot.send_chat_action(message.chat.id, 'typing')

    try:
        answer = ask_ai(role, department, question)
        bot.reply_to(message, answer)
    except Exception as e:
        print(f"AI error: {e}")
        bot.reply_to(message, "Произошла ошибка при обращении к AI.")


if __name__ == '__main__':
    create_table_if_not_exists()
    bot.polling()
