from openai import OpenAI  
from dotenv import load_dotenv
import os
from admin.db import update_department_model

load_dotenv()
ai_token = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=ai_token,
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "save_model_for_department",
            "description": "Сохраняет модель, выбранную для отдела",
            "parameters": {
                "type": "object",
                "properties": {
                    "department_name": {"type": "string"},
                    "model_name": {"type": "string"},
                },
                "required": ["department_name", "model_name"]
            }
        }
    }
]

# agents/model_selector.py

def save_model_for_department(department_name: str, model_name: str):
    update_department_model(department_name, model_name)
    return f"✅ Модель '{model_name}' сохранена для отдела '{department_name}'"


def run_model_selection_agent(department_name: str, description: str):
    system_prompt = (
        "Ты — помощник, который выбирает лучшую LLM-модель для отдела компании "
        "и сохраняет её вызовом функции. "
        "Выбор осуществляем с учётом необходимости мощности модели для задач отдела, например для"
        "разработки и приближенного лучше использовать наиболее мощные, для аналитики тестировки и тд - средние"
        "ну и для hr, маргетинга и тд - самые простые модельки."
        "У тебя есть следующие доступные модели: "
        "- deepseek/deepseek-chat-v3-0324:free\n"
        "- qwen/qwq-32b:free\n"
        "- mistralai/mistral-nemo:free\n"
        "- google/gemma-3-27b-it:free\n"
        "Выбери подходящую модель в зависимости от описания отдела."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Описание отдела: {description}\nНазвание: {department_name}"},
    ]

    response = client.chat.completions.create(
        model="deepseek/deepseek-chat-v3-0324:free",  # начальная модель для reasoning
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    tool_call = response.choices[0].message.tool_calls[0]
    if tool_call.function.name == "save_model_for_department":
        args = eval(tool_call.function.arguments)
        return save_model_for_department(**args)
