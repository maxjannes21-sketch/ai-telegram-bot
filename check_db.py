import db

conn = db.get_connection()
cursor = conn.cursor()

print("=== Пользователи ===")
cursor.execute("SELECT id, telegram_id, username FROM users")
for row in cursor.fetchall():
    print(row)

print("\n=== Сообщения ===")
cursor.execute("""
    SELECT m.id, u.username, m.message_text, m.created_at
    FROM messages m
    JOIN users u ON m.user_id = u.id
    ORDER BY m.created_at DESC
    LIMIT 5
""")
for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()