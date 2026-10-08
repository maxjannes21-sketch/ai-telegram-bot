"""Одноразовый скрипт: создаёт таблицу для базы знаний."""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password=os.getenv("DB_PASSWORD")
)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_chunks (
        id SERIAL PRIMARY KEY,
        chunk_text TEXT NOT NULL,
        embedding JSONB NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
    )
""")

conn.commit()
cursor.close()
conn.close()
print("Таблица knowledge_chunks создана!")