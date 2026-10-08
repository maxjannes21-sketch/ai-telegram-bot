import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": os.getenv("DB_PASSWORD")
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def get_or_create_user(telegram_id: int, username: str) -> int:
    """Находит пользователя по telegram_id или создаёт нового.
    Возвращает id пользователя в базе."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (telegram_id, username)
        VALUES (%s, %s)
        ON CONFLICT (telegram_id) DO NOTHING
    """, (telegram_id, username))
    conn.commit()

    cursor.execute(
        "SELECT id FROM users WHERE telegram_id = %s",
        (telegram_id,)
    )
    user_id = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return user_id

def save_message(user_id: int, message_text: str, bot_reply: str):
    """Сохраняет сообщение пользователя и ответ бота."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (user_id, message_text, bot_reply)
        VALUES (%s, %s, %s)
    """, (user_id, message_text, bot_reply))
    conn.commit()

    cursor.close()
    conn.close()
def get_recent_messages(user_id: int, limit: int = 10):
    """Возвращает последние limit сообщений пользователя (от старых к новым)."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT message_text, bot_reply
        FROM messages
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT %s
    """, (user_id, limit))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    rows.reverse()
    return rows
def get_stats():
    """Возвращает статистику бота из базы."""
    conn = get_connection()
    cursor = conn.cursor()

    # Всего пользователей
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    # Всего сообщений
    cursor.execute("SELECT COUNT(*) FROM messages")
    total_messages = cursor.fetchone()[0]

    # Сообщений сегодня
    cursor.execute("""
        SELECT COUNT(*) FROM messages
        WHERE created_at::date = CURRENT_DATE
    """)
    today_messages = cursor.fetchone()[0]

    # Топ-3 пользователя по количеству сообщений
    cursor.execute("""
        SELECT u.username, COUNT(m.id) AS msg_count
        FROM users u
        JOIN messages m ON m.user_id = u.id
        GROUP BY u.username
        ORDER BY msg_count DESC
        LIMIT 3
    """)
    top_users = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "total_users": total_users,
        "total_messages": total_messages,
        "today_messages": today_messages,
        "top_users": top_users,
    }
def get_all_users():
    """Все пользователи из базы."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, telegram_id, username, created_at
        FROM users
        ORDER BY created_at DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            "id": r[0],
            "telegram_id": r[1],
            "username": r[2],
            "created_at": r[3].isoformat()
        }
        for r in rows
    ]

def get_user_messages(user_id: int):
    """Все сообщения конкретного пользователя."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.id, m.message_text, m.bot_reply, m.created_at
        FROM messages m
        WHERE m.user_id = %s
        ORDER BY m.created_at
    """, (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            "id": r[0],
            "message": r[1],
            "reply": r[2],
            "created_at": r[3].isoformat()
        }
        for r in rows
    ]