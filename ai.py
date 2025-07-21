from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
import os
from db import get_department_description, get_recent_messages, get_department_model

load_dotenv()

# Загружаем список ключей из .env
OPENROUTER_KEYS = os.getenv("OPENROUTER_KEYS", "").split(",")

# Контекст компании
with open("company_context.txt", "r", encoding="utf-8") as f:
    COMPANY_CONTEXT = f.read()


def get_available_client() -> OpenAI:
    """
    Возвращает первый доступный OpenAI client с рабочим ключом.
    """
    for key in OPENROUTER_KEYS:
        try:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=key.strip(),
            )
            # Пробный недорогой запрос, чтобы проверить ключ (в идеале lightweight модель)
            client.chat.completions.create(
                model="mistralai/mistral-7b-instruct:free",
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1,
            )
            return client
        except Exception as e:
            print(f"[⚠️] Ключ {key.strip()} не работает: {e}")
            continue
    raise RuntimeError("❌ Нет доступных OpenRouter API ключей!")


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

    # Модель из БД, или дефолт
    model_name = get_department_model(department) or "deepseek/deepseek-chat-v3-0324:free"

    client = get_available_client()

    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        extra_headers={
            "HTTP-Referer": "https://yourproject.com",
            "X-Title": "AI Assistant Bot",
        },
    )

    return response.choices[0].message.content
