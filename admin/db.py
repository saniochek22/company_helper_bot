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
            name TEXT UNIQUE NOT NULL
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


# Добавить отдел
def create_department(name: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO departments (name)
        VALUES (%s)
        ON CONFLICT (name) DO NOTHING
    """, (name,))
    conn.commit()
    cur.close()
    conn.close()


# Получить все отделы
def get_all_departments():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM departments")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

