import psycopg2
import os
from dotenv import load_dotenv
from .models import UserCreate, UserUpdate

load_dotenv()

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def create_user(user: UserCreate):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (telegram_id, username, role, department)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (telegram_id) DO NOTHING
    """, (user.telegram_id, user.username, user.role, user.department))
    conn.commit()
    cur.close()
    conn.close()


def get_user(telegram_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT telegram_id, username, role, department FROM users WHERE telegram_id = %s", (telegram_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def update_user(telegram_id: int, user: UserUpdate):
    conn = get_connection()
    cur = conn.cursor()
    if user.role:
        cur.execute("UPDATE users SET role = %s WHERE telegram_id = %s", (user.role, telegram_id))
    if user.department:
        cur.execute("UPDATE users SET department = %s WHERE telegram_id = %s", (user.department, telegram_id))
    if user.username:
        cur.execute("UPDATE users SET username = %s WHERE telegram_id = %s", (user.username, telegram_id))
    conn.commit()
    cur.close()
    conn.close()


def delete_user(telegram_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE telegram_id = %s", (telegram_id,))
    conn.commit()
    cur.close()
    conn.close()

def get_all_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT telegram_id, username, role, department FROM users")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# Инициализация таблицы departments
def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id BIGINT PRIMARY KEY,
            username TEXT,
            role TEXT,
            department TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            description_for_ai TEXT DEFAULT ''
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_message_history (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT NOT NULL,
            role TEXT,
            department TEXT,
            message_type TEXT CHECK (message_type IN ('user', 'assistant')),
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


# Добавить отдел
def create_department(name: str, description_for_ai: str | None = None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO departments (name, description_for_ai)
        VALUES (%s, %s)
        ON CONFLICT (name) DO UPDATE SET description_for_ai = COALESCE(EXCLUDED.description_for_ai, departments.description_for_ai)
    """, (name, description_for_ai))
    conn.commit()
    cur.close()
    conn.close()

def update_department(department_id: int, name: str, description_for_ai: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE departments
        SET name = %s, description_for_ai = %s
        WHERE id = %s
    """, (name, description_for_ai, department_id))
    conn.commit()
    cur.close()
    conn.close()

def delete_department(department_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM departments WHERE id = %s", (department_id,))
    conn.commit()
    cur.close()
    conn.close()



# Получить все отделы
def get_all_departments():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, description_for_ai FROM departments")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

