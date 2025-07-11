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
        INSERT INTO users (telegram_id, role, department)
        VALUES (%s, %s, %s)
        ON CONFLICT (telegram_id) DO NOTHING
    """, (user.telegram_id, user.role, user.department))
    conn.commit()
    cur.close()
    conn.close()

def get_user(telegram_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT telegram_id, role, department FROM users WHERE telegram_id = %s", (telegram_id,))
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
    cur.execute("SELECT telegram_id, role, department FROM users")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
