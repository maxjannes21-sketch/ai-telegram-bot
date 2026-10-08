from sentence_transformers import SentenceTransformer
import numpy as np

print("Загружаю модель эмбеддингов... (первый раз — долго, качается ~450 МБ)")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print("Модель загружена!")

# Читаем базу знаний и режем на кусочки по пустым строкам
with open('knowledge.txt', encoding='utf-8') as f:
    chunks = [c.strip() for c in f.read().split('\n\n') if c.strip()]

print(f"База знаний: {len(chunks)} фрагментов")

# Превращаем каждый фрагмент в вектор
embeddings = model.encode(chunks)

while True:
    question = input("\nВопрос (или 'выход'): ")
    if question.lower() == 'выход':
        break

    q_emb = model.encode([question])[0]

    # Косинусная близость к каждому фрагменту
    sims = []
    for emb in embeddings:
        sim = np.dot(q_emb, emb) / (np.linalg.norm(q_emb) * np.linalg.norm(emb))
        sims.append(sim)

    best = int(np.argmax(sims))
    print(f"\n→ Схожесть: {sims[best]:.2f}")
    print(f"→ Найденный фрагмент:\n{chunks[best]}")