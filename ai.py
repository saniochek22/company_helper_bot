from openai import OpenAI
from dotenv import load_dotenv
import os
from db import get_department_description, get_recent_messages, get_department_model  # добавь функцию
load_dotenv()

ai_token = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=ai_token,
)

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

    history = get_recent_messages(telegram_id, limit=10)

    messages = [{"role": "system", "content": system_prompt}] + history
    messages.append({"role": "user", "content": question})

    # Берём модель из базы, если нет — дефолт
    model_name = get_department_model(department)
    if not model_name:
        model_name = "deepseek/deepseek-chat-v3-0324:free"

    completion = client.chat.completions.create(
        model=model_name,
        messages=messages,
        extra_headers={
            "HTTP-Referer": "https://yourproject.com",
            "X-Title": "AI Assistant Bot",
        },
    )

    return completion.choices[0].message.content
