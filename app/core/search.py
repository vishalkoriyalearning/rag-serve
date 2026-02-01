import numpy as np
from app.core.embeddings import embed_chunks
from app.core.vectorstore import load_faiss_index, load_chunks
from app.core.generator import call_openai, call_ollama
from app.utils.logging import get_logger
import os
from dotenv import load_dotenv

load_dotenv()

logger = get_logger()


PLATFORM = os.getenv("PLATFORM", "LOCAL")


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

def generate_answer(query: str, top_k: int = 5, api_key: str = None):
    # 1) Retrieve
    emb = embed_chunks([query])
    index = load_faiss_index()
    chunks = load_chunks()
    
    if index is None or len(chunks) == 0:
        return {"error": "Index not built. Use /index-doc first."}
    
    _, indices = index.search(emb, top_k)

    context = "\n∎\n".join(chunks[i] for i in indices[0])
    prompt = f"Context:\n{context}\n\nQuestion:\n{query}"

    if PLATFORM == "LOCAL":
        # Local: Try OpenAI first (with user's API key), fallback to Ollama
        try:
            logger.info("Trying with OpenAI")
            if api_key:
                out = call_openai(prompt, api_key=api_key)
            else:
                # Use API key from .env if available
                out = call_openai(prompt)
            
            if out:
                return {"response": out, "source": "openai"}
        except Exception as e:
            logger.warning(f"OpenAI call failed: {e}. Falling back to Ollama.")
        
        # Fallback to Ollama in LOCAL mode
        try:
            logger.info("Trying with Ollama")
            fallback = call_ollama(prompt)
            return {"response": fallback, "source": "ollama"}
        except Exception as e:
            logger.error(f"Both OpenAI and Ollama failed: {e}")
            return {"error": f"Generation failed: {str(e)}"}
    
    else:
        # Cloud: Use OpenAI only (no fallback)
        try:
            if api_key:
                out = call_openai(prompt, api_key=api_key)
            else:
                out = call_openai(prompt)
            return {"response": out, "source": "openai"}
        except Exception as e:
            logger.error(f"OpenAI call failed in CLOUD mode: {e}")
            return {"error": f"Generation failed: {str(e)}"}