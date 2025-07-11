from fastapi import FastAPI, HTTPException
from . import db, models

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
    return {"telegram_id": data[0], "role": data[1], "department": data[2]}

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
    return [{"telegram_id": r[0], "role": r[1], "department": r[2]} for r in rows]
