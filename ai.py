from openai import OpenAI
from dotenv import load_dotenv
import os
from db import get_department_description, get_recent_messages, get_department_model

load_dotenv()

# Загружаем контекст компании из файла
with open("company_context.txt", "r", encoding="utf-8") as f:
    COMPANY_CONTEXT = f.read()


def ask_ai(role: str, department: str, question: str, telegram_id: int) -> str:
    # Получаем описание отдела из БД
    department_description = get_department_description(department)
    dept_info = f"Описание отдела: {department_description}" if department_description else ""

    # Формируем системный промпт с контекстом компании и описанием отдела
    system_prompt = f"""
Ты — AI-помощник внутри компании. Отвечай профессионально, кратко и понятно, с опорой на внутренние документы и процессы.

Контекст компании:
{COMPANY_CONTEXT}

{dept_info}

Если информация в вопросе не соответствует корпоративной тематике, вежливо откажись отвечать.

Роль сотрудника, задающего вопрос: {role} в отделе {department}.
""".strip()

    # Получаем историю сообщений для пользователя
    history = get_recent_messages(telegram_id, limit=10)  # список dict с keys: role и content

    # Формируем сообщения для отправки в OpenAI chat API
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)  # добавляем историю
    messages.append({"role": "user", "content": question})

    # Получаем модель для отдела из БД, если нет — дефолтная
    model_name = get_department_model(department) or "gpt-3.5-turbo"

    # Инициализируем клиента OpenAI с ключом из env
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Отправляем запрос в OpenAI chat completion
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        extra_headers={
            "HTTP-Referer": "https://yourproject.com",
            "X-Title": "AI Assistant Bot",
        },
    )

    return response.choices[0].message.content
