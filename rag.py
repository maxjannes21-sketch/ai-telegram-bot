from sentence_transformers import SentenceTransformer
import numpy as np

print("Загружаю модель эмбеддингов...")

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

with open('knowledge.txt', encoding='utf-8') as f:
    chunks = [c.strip() for c in f.read().split('\n\n') if c.strip()]

embeddings = model.encode(chunks)

print(f"База знаний загружена: {len(chunks)} фрагментов")

def find_relevant(question: str, top_k: int = 2):
    """Находит top_k самых релевантных фрагментов из базы знаний."""
    q_emb = model.encode([question])[0]

    sims = []
    for i, emb in enumerate(embeddings):
        sim = np.dot(q_emb, emb) / (np.linalg.norm(q_emb) * np.linalg.norm(emb))
        sims.append((float(sim), i))

    sims.sort(reverse=True)
    return [(chunks[i], sim) for sim, i in sims[:top_k]]