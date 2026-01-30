import json
import numpy as np
from app.core.vectorstore import load_faiss_index, load_chunks
from app.core.embeddings import embed_chunks

def recall_at_k(query, answer_text, k=5):
    emb = embed_chunks([query])
    index = load_faiss_index()
    chunks = load_chunks()

    _, indices = index.search(emb, k)
    retrieved = [chunks[i] for i in indices[0]]

    return any(answer_text.lower() in chunk.lower() for chunk in retrieved)

if __name__ == "__main__":
    tests = [
        ("What is AI?", "AI is ..."),
        ("What is chatbot?", "A chatbot is ..."),
    ]

    scores = [recall_at_k(q, ans) for q, ans in tests]
    print("Recall@5:", sum(scores) / len(scores))
