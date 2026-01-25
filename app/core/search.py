import numpy as np
from app.core.embeddings import embed_chunks
from app.core.vectorstore import load_faiss_index, load_chunks
from app.core.generator import call_openai, call_ollama

def search(query: str, top_k: int = 5):
    # Embed query text into vector
    query_emb = embed_chunks([query])
    query_emb = np.array(query_emb).astype("float32")

    index = load_faiss_index()
    chunks = load_chunks()

    if index is None or len(chunks) == 0:
        return {"error": "Index not built. Use /index-doc first."}

    distances, indices = index.search(query_emb, top_k)
    indices = indices[0]
    distances = distances[0]

    results = []
    for idx, dist in zip(indices, distances):
        results.append({
            "chunk_index": int(idx),
            "text": chunks[idx],
            "distance": float(dist)
        })

    return {"results": results}

def generate_answer(query: str, top_k: int = 5):
    # 1) Retrieve
    emb = embed_chunks([query])
    index = load_faiss_index()
    chunks = load_chunks()
    _, indices = index.search(emb, top_k)

    context = "\n∎\n".join(chunks[i] for i in indices[0])
    prompt = f"Context:\n{context}\n\nQuestion:\n{query}"

    # 2) Try OpenAI
    out = call_openai(prompt)
    if out:
        return {"response": out, "source": "openai"}

    # 3) Fallback to Ollama
    fallback = call_ollama(prompt)
    return {"response": fallback, "source": "ollama"}