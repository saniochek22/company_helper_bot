import os
from fastapi import FastAPI, HTTPException, APIRouter, UploadFile, File, Depends, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, PlainTextResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from cryptography.fernet import Fernet

from . import db, models
from .db import get_connection, init_db
from .models import BotTokenInput, DepartmentCreate, DepartmentOut
from .pdf_handler import process_pdf_upload
from agents.model_selector import run_model_selection_agent

from fastapi.staticfiles import StaticFiles
import os

load_dotenv()

init_db()

app = FastAPI(title="Admin API", description="Управление пользователями бота", version="1.0")
router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory="frontend")

STATIC_DIR = os.path.join(BASE_DIR, "..", "frontend", "static")  

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

fernet = Fernet(os.getenv("FERNET_SECRET_KEY").encode())
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

def encrypt_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()

def decrypt_token(token_encrypted: str) -> str:
    return fernet.decrypt(token_encrypted.encode()).decode()

def is_authenticated(request: Request):
    return request.session.get("user") == os.getenv("ADMIN_USERNAME")

def require_auth(request: Request):
    if not is_authenticated(request):
        raise HTTPException(status_code=403, detail="Not authenticated")

# ---- User routes ----

@router.post("/users/", response_model=models.UserOut, dependencies=[Depends(require_auth)])
def create_user(user: models.UserCreate):
    db.create_user(user)
    return user

@router.get("/users/{telegram_id}", response_model=models.UserOut, dependencies=[Depends(require_auth)])
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

@router.patch("/users/{telegram_id}", dependencies=[Depends(require_auth)])
def update_user(telegram_id: int, user: models.UserUpdate):
    db.update_user(telegram_id, user)
    return {"message": "User updated"}

@router.delete("/users/{telegram_id}", dependencies=[Depends(require_auth)])
def delete_user(telegram_id: int):
    db.delete_user(telegram_id)
    return {"message": "User deleted"}

@router.get("/users/", response_model=list[models.UserOut], dependencies=[Depends(require_auth)])
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

# ---- Bot config ----

@router.post("/config/bot-token", dependencies=[Depends(require_auth)])
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

# ---- Department routes ----

@router.post("/departments/", response_model=None, dependencies=[Depends(require_auth)])
def add_department(dept: DepartmentCreate, background_tasks: BackgroundTasks):
    db.create_department(dept.name, dept.description_for_ai)
    background_tasks.add_task(run_model_selection_agent, dept.name, dept.description_for_ai)
    return {"message": "Department added"}

@router.get("/departments/{department_id}", response_model=DepartmentOut, dependencies=[Depends(require_auth)])
def get_department(department_id: int):
    department = db.get_department(department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return {"id": department[0], "name": department[1], "description_for_ai": department[2]}

@router.patch("/departments/{department_id}", dependencies=[Depends(require_auth)])
def update_department(department_id: int, dept: DepartmentCreate):
    db.update_department(department_id, dept.name, dept.description_for_ai)
    return {"message": "Department updated"}

@router.delete("/departments/{department_id}", dependencies=[Depends(require_auth)])
def delete_department(department_id: int):
    db.delete_department(department_id)
    return {"message": "Department deleted"}

@router.get("/departments/", response_model=list[DepartmentOut], dependencies=[Depends(require_auth)])
def list_departments():
    departments = db.get_all_departments()
    return [
        {"id": d[0], "name": d[1], "description_for_ai": d[2]} 
        for d in departments
    ]

@router.post("/departments/{department_id}/upload-description/", dependencies=[Depends(require_auth)])
async def upload_pdf_description(department_id: int, file: UploadFile = File(...)):
    result = process_pdf_upload(department_id, file)
    return result

# ---- Frontend routes (no /api prefix!) ----

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    if not is_authenticated(request):
        return RedirectResponse("/login", status_code=302)
    return templates.TemplateResponse("index.html", {"request": request, "user": request.session.get("user")})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == os.getenv("ADMIN_USERNAME") and password == os.getenv("ADMIN_PASSWORD"):
        request.session["user"] = username
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Неверные данные"})

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)

# ---- Health check ----

@app.get("/health")
def health_check():
    return {"status": "ok"}

# ---- Error handler for 404 ----

from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exception_handlers import http_exception_handler

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    if exc.status_code == 404:
        return PlainTextResponse("\u0421\u0442\u0440\u0430\u043d\u0438\u0446\u0430 \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u0430", status_code=404)
    return await http_exception_handler(request, exc)

# ---- Register router with /api prefix ----

app.include_router(router, prefix="/api")