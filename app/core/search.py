import numpy as np
from app.core.embeddings import embed_chunks
from app.core.vectorstore import load_faiss_index, load_chunks

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
