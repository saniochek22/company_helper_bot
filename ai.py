from openai import OpenAI
from dotenv import load_dotenv
import os
from db import get_department_description, get_recent_messages

load_dotenv()
ai_token = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=ai_token,
)

# Загружаем контекст компании один раз при запуске
with open("company_context.txt", "r", encoding="utf-8") as f:
    COMPANY_CONTEXT = f.read()

def ask_ai(role: str, department: str, question: str, telegram_id: int) -> str:
    department_description = get_department_description(department)
    dept_info = f"Описание отдела: {department_description}" if department_description else ""

    system_prompt = f"""
Ты — AI-помощник внутри компании. Отвечай профессионально, кратко и понятно, с опорой на внутренние документы и процессы.

Контекст компании:
{COMPANY_CONTEXT}

{dept_info}

Если информация в вопросе не соответствует корпоративной тематике, вежливо откажись отвечать.

Роль сотрудника, задающего вопрос: {role} в отделе {department}.
""".strip()

    # История диалога
    history = get_recent_messages(telegram_id, limit=10)

    messages = [{"role": "system", "content": system_prompt}] + history
    messages.append({"role": "user", "content": question})

    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "https://yourproject.com",
            "X-Title": "AI Assistant Bot",
        },
        model="deepseek/deepseek-chat-v3-0324:free",
        messages=messages
    )

    return completion.choices[0].message.content

