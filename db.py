import psycopg2

def create_table_if_not_exists():
    conn = get_connection()
    cur = conn.cursor()

    # Создаём таблицу, если её нет
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id BIGINT PRIMARY KEY,
            role TEXT,
            department TEXT
        )
    """)

    # Добавляем колонку department, если она ещё не существует
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

    conn.commit()
    cur.close()
    conn.close()


# Подключение к БД
def get_connection():
    return psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="localhost",  # или имя контейнера в Docker: db
        port="5432"
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

