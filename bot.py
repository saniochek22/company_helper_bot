import telebot
from db import create_table_if_not_exists, get_user_role, get_user_department
from ai import ask_ai
from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "Привет! Я AI-ассистент. Просто задай свой вопрос, и я постараюсь помочь.\n"
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
