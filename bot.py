import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from db import save_user_role, create_table_if_not_exists, save_user_department, get_user_department
from ai import ask_ai
from db import get_user_role
from telebot import types


# 🔑 Токен
TOKEN = '7310104929:AAFQ275lxn5YJvitmZ-G96NQsBolI16LGZc'
bot = telebot.TeleBot(TOKEN)

# Профессии
professions = ['Программист', 'Дизайнер', 'Маркетолог', 'Менеджер', 'Аналитик']
departments = ["Продажи", "Маркетинг", "Разработка", "HR", "Финансы"]


# Обработка команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    for prof in professions:
        markup.add(InlineKeyboardButton(text=prof, callback_data=f"profession_{prof}"))
    bot.send_message(message.chat.id, "Привет, я ai-ассистент, обладаю всей информацией о текущем положении дел в компании и с удовольствием отвечу на твой вопрос. Выберите вашу профессию:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('profession_'))
def handle_profession_choice(call):
    chosen_prof = call.data.split("_", 1)[1]
    telegram_id = call.from_user.id 

    save_user_role(telegram_id, chosen_prof)

    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Вы выбрали профессию: {chosen_prof}"
    )

    markup = types.InlineKeyboardMarkup()
    for dept in departments:
        markup.add(types.InlineKeyboardButton(text=dept, callback_data=f"department_{dept}"))

    bot.send_message(call.message.chat.id, "Теперь выберите свой отдел:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('department_'))
def handle_department_choice(call):
    chosen_dept = call.data.split("_", 1)[1]
    telegram_id = call.from_user.id

    save_user_department(telegram_id, chosen_dept)

    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Вы выбрали отдел: {chosen_dept}.\nТеперь можете задать вопрос своему AI-помощнику."
    )


@bot.message_handler(func=lambda msg: True)
def handle_user_question(message):
    user_id = message.from_user.id
    role = get_user_role(user_id)
    department = get_user_department(user_id)

    if not role:
        bot.reply_to(message, "Пожалуйста, выбери свою профессию, прежде чем задавать вопросы.")
        return

    if not department:
        bot.reply_to(message, "Пожалуйста, выбери свой отдел, прежде чем задавать вопросы.")
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
