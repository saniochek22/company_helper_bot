import psycopg2
from dotenv import load_dotenv
import os
from cryptography.fernet import Fernet

def create_bot_config_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bot_config (
            id SERIAL PRIMARY KEY,
            bot_token TEXT NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def create_table_if_not_exists():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id BIGINT PRIMARY KEY,
            role TEXT,
            department TEXT
        )
    """)

    cur.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'department'
            ) THEN
                ALTER TABLE users ADD COLUMN department TEXT;
            END IF;
        END
        $$;
    """)

    cur.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'username'
            ) THEN
                ALTER TABLE users ADD COLUMN username TEXT;
            END IF;
        END
        $$;
    """)


    conn.commit()
    cur.close()
    conn.close()


def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

# Сохранить или обновить роль пользователя
def save_user_role(telegram_id, role):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (telegram_id, role)
        VALUES (%s, %s)
        ON CONFLICT (telegram_id)
        DO UPDATE SET role = EXCLUDED.role
    """, (telegram_id, role))
    conn.commit()
    cur.close()
    conn.close()

def get_user_role(telegram_id):
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT role FROM users WHERE telegram_id = %s", (telegram_id,))
            result = cur.fetchone()
            return result[0] if result else None

def save_user_department(telegram_id: int, department: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users
        SET department = %s
        WHERE telegram_id = %s
    """, (department, telegram_id))
    conn.commit()
    cur.close()
    conn.close()

def get_user_department(telegram_id: int) -> str | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT department FROM users WHERE telegram_id = %s
    """, (telegram_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result else None


def save_user_info(telegram_id: int, username: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (telegram_id, username)
        VALUES (%s, %s)
        ON CONFLICT (telegram_id)
        DO UPDATE SET username = EXCLUDED.username
    """, (telegram_id, username))
    conn.commit()
    cur.close()
    conn.close()

def user_exists(telegram_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE telegram_id = %s", (telegram_id,))
    exists = cur.fetchone() is not None
    cur.close()
    conn.close()
    return exists

def get_decrypted_bot_token():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT bot_token FROM bot_config ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise Exception("Токен не найден в базе.")
    fernet = Fernet(os.getenv("FERNET_SECRET_KEY").encode())
    return fernet.decrypt(row[0].encode()).decode()

def get_department_description(department_name: str) -> str | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT description_for_ai FROM departments WHERE name = %s", (department_name,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else None

def get_department_model(department_name: str) -> str | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT model FROM departments WHERE name = %s", (department_name,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row and row[0]:
        return row[0]
    return None


def save_message(telegram_id: int, role: str, department: str, content: str, message_type: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO user_message_history (
            telegram_id, role, department, message_type, content
        ) VALUES (%s, %s, %s, %s, %s)
    """, (telegram_id, role, department, message_type, content))
    conn.commit()
    cur.close()
    conn.close()
    cleanup_old_messages(telegram_id)

def get_recent_messages(telegram_id: int, limit: int = 10) -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT message_type, content FROM user_message_history
        WHERE telegram_id = %s
        ORDER BY created_at DESC
        LIMIT %s
    """, (telegram_id, limit))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

def cleanup_old_messages(telegram_id: int, keep_last_n: int = 10):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM user_message_history
        WHERE id IN (
            SELECT id FROM user_message_history
            WHERE telegram_id = %s
            ORDER BY created_at DESC
            OFFSET %s
        )
    """, (telegram_id, keep_last_n))
    conn.commit()
    cur.close()
    conn.close()
