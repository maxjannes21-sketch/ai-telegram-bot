import psycopg2
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

def _load_from_db():
    """Загружает чанки и эмбеддинги из PostgreSQL при старте."""
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password=os.getenv("DB_PASSWORD")
    )
    cursor = conn.cursor()
    cursor.execute("SELECT chunk_text, embedding FROM knowledge_chunks ORDER BY id")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    chunks = [row[0] for row in rows]
    embeddings = np.array([row[1] for row in rows])  # JSONB возвращается уже списком
    return chunks, embeddings

chunks, embeddings = _load_from_db()
print(f"RAG: загружено {len(chunks)} чанков из базы")

def find_relevant(question: str, top_k: int = 2):
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    q_emb = model.encode([question])[0]
    sims = []
    for i, emb in enumerate(embeddings):
        sim = np.dot(q_emb, emb) / (np.linalg.norm(q_emb) * np.linalg.norm(emb))
        sims.append((float(sim), i))
    sims.sort(reverse=True)
    return [(chunks[i], sim) for sim, i in sims[:top_k]]