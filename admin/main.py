from fastapi import FastAPI, HTTPException
from . import db, models
from cryptography.fernet import Fernet
import os
from .models import BotTokenInput
from .db import get_connection
from .models import DepartmentCreate, DepartmentOut
from .db import init_db

init_db()



fernet = Fernet(os.getenv("FERNET_SECRET_KEY").encode())

def encrypt_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()

def decrypt_token(token_encrypted: str) -> str:
    return fernet.decrypt(token_encrypted.encode()).decode()


app = FastAPI(title="Admin API", description="Управление пользователями бота", version="1.0")

@app.post("/users/", response_model=models.UserOut)
def create_user(user: models.UserCreate):
    db.create_user(user)
    return user

@app.get("/users/{telegram_id}", response_model=models.UserOut)
def read_user(telegram_id: int):
    data = db.get_user(telegram_id)
    if not data:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "telegram_id": data[0],
        "username": data[1],
        "role": data[2],
        "department": data[3]
    }


@app.patch("/users/{telegram_id}")
def update_user(telegram_id: int, user: models.UserUpdate):
    db.update_user(telegram_id, user)
    return {"message": "User updated"}

@app.delete("/users/{telegram_id}")
def delete_user(telegram_id: int):
    db.delete_user(telegram_id)
    return {"message": "User deleted"}

@app.get("/users/", response_model=list[models.UserOut])
def list_users():
    rows = db.get_all_users()
    return [
        {
            "telegram_id": r[0],
            "username": r[1],
            "role": r[2] or "",
            "department": r[3] or ""
        }
        for r in rows
    ]


# FastAPI route (в admin)
@app.post("/config/bot-token")
def set_bot_token(data: BotTokenInput):
    encrypted_token = encrypt_token(data.token)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM bot_config")
    cur.execute("INSERT INTO bot_config (bot_token) VALUES (%s)", (encrypted_token,))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Encrypted bot token saved"}


@app.post("/departments/", response_model=None)
def add_department(dept: DepartmentCreate):
    db.create_department(dept.name)
    return {"message": "Department added"}

@app.get("/departments/", response_model=list[DepartmentOut])
def list_departments():
    departments = db.get_all_departments()
    return [{"id": d[0], "name": d[1]} for d in departments]