"""Читает knowledge.txt, считает эмбеддинги и кладёт всё в PostgreSQL."""
import psycopg2
import json
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

# Читаем и нарезаем базу знаний (как раньше в rag.py)
with open('knowledge.txt', encoding='utf-8') as f:
    chunks = [c.strip() for c in f.read().split('\n\n') if c.strip()]

print(f"Найдено чанков: {len(chunks)}")

# Считаем эмбеддинги
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
embeddings = model.encode(chunks)

# Кладём в базу
conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password=os.getenv("DB_PASSWORD")
)
cursor = conn.cursor()

# Очищаем таблицу, чтобы при повторном запуске не было дублей
cursor.execute("DELETE FROM knowledge_chunks")

for chunk, emb in zip(chunks, embeddings):
    cursor.execute(
        "INSERT INTO knowledge_chunks (chunk_text, embedding) VALUES (%s, %s)",
        (chunk, json.dumps(emb.tolist()))
    )

conn.commit()
cursor.close()
conn.close()
print(f"Загружено {len(chunks)} чанков в базу!")