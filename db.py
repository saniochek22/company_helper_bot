import psycopg2

def create_table_if_not_exists():
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            # Создаем таблицу, если её нет
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id BIGINT PRIMARY KEY,
                    role TEXT NOT NULL
                )
            """)
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

