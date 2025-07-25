from openai import OpenAI
from dotenv import load_dotenv
import os
from admin.db import update_department_model, update_department_assistant_id

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Маппинг модели по типу отдела
MODEL_RECOMMENDATIONS = {
    "разработка": "gpt-3.5-turbo" ,
    "аналитика": "gpt-3.5-turbo" ,
    "тестирование": "gpt-3.5-turbo" ,
    "hr": "gpt-3.5-turbo" ,
    "маркетинг": "gpt-3.5-turbo" ,
}

def select_model(description: str) -> str:
    desc = description.lower()
    for key, model in MODEL_RECOMMENDATIONS.items():
        if key in desc:
            return model
    return "gpt-3.5-turbo" 

def create_assistant_for_department(name: str, description: str, model_name: str):
    assistant = client.beta.assistants.create(
        name=f"Агент отдела {name}",
        instructions=(
            f"Ты — персональный AI-помощник для отдела '{name}'. "
            f"Описание отдела: {description}. "
            f"Отвечай кратко, профессионально, по делу."
        ),
        tools=[],
        model=model_name
    )
    return assistant.id

def run_model_selection_agent(department_name: str, description: str):
    model_name = select_model(description)
    assistant_id = create_assistant_for_department(department_name, description, model_name)

    # Сохраняем и модель, и ассистента
    update_department_model(department_name, model_name)
    update_department_assistant_id(department_name, assistant_id)

    return f"✅ Для отдела '{department_name}' выбрана модель: {model_name}, создан агент {assistant_id}"
