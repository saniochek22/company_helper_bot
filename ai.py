from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
ai_token = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=ai_token,
)

# Загружаем контекст компании один раз при запуске
with open("company_context.txt", "r", encoding="utf-8") as f:
    COMPANY_CONTEXT = f.read()

def ask_ai(role: str, department:str, question: str) -> str:
    system_prompt = f"""
Ты — AI-помощник внутри компании. Отвечай профессионально, кратко и понятно, с опорой на внутренние документы и процессы.

Контекст компании:
{COMPANY_CONTEXT}

Если информация в вопросе не соответствует корпоративной тематике, вежливо откажись отвечать.

Роль сотрудника, задающего вопрос: {role} в отделе {department}.
"""

    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "https://yourproject.com",
            "X-Title": "AI Assistant Bot",
        },
        model="openrouter/cypher-alpha:free",
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": question}
        ]
    )

    return completion.choices[0].message.content
