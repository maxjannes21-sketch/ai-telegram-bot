import psycopg2

# Подключение к базе
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="postgres",      # база по умолчанию
    user="postgres",
    password="Pti4ko40"    # пароль из шага 2
)
cursor = conn.cursor()

# Создаём таблицу пользователей (если её ещё нет)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT UNIQUE,
        username VARCHAR(100),
        created_at TIMESTAMP DEFAULT NOW()
    )
""")

# Создаём таблицу сообщений
cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        message_text TEXT,
        bot_reply TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    )
""")

conn.commit()
print("✅ Таблицы созданы!")

# Тестовая запись: добавим пользователя
cursor.execute("""
    INSERT INTO users (telegram_id, username)
    VALUES (123456789, 'test_user')
    ON CONFLICT (telegram_id) DO NOTHING
""")
conn.commit()

# Читаем обратно
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
print("Пользователи в базе:")
for row in rows:
    print(row)

cursor.close()
conn.close()