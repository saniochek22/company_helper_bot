from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

# Загружаем контекст компании один раз при запуске
with open("company_context.txt", "r", encoding="utf-8") as f:
    COMPANY_CONTEXT = f.read()

def ask_ai(role: str, question: str) -> str:
    system_prompt = f"""
Ты — AI-помощник внутри компании. Отвечай профессионально, кратко и понятно, с опорой на внутренние документы и процессы.

Контекст компании:
{COMPANY_CONTEXT}

Если информация в вопросе не соответствует корпоративной тематике, вежливо откажись отвечать.

Роль сотрудника, задающего вопрос: {role}
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
