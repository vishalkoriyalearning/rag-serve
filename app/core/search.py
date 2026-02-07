import numpy as np
from app.core.embeddings import embed_chunks
from app.core.vectorstore import load_faiss_index, load_chunks
from app.core.generator import call_openai, call_gemini
from app.utils.logging import get_logger
from dotenv import load_dotenv

load_dotenv()

logger = get_logger()



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

def generate_answer(query: str, top_k: int = 5, llm_provider: str = None, api_key: str = None):
    # 1) Retrieve
    emb = embed_chunks([query])
    index = load_faiss_index()
    chunks = load_chunks()
    
    if index is None or len(chunks) == 0:
        return {"error": "Index not built. Use /index-doc first."}
    
    _, indices = index.search(emb, top_k)

    context = "\n∎\n".join(chunks[i] for i in indices[0])
    prompt = f"Context:\n{context}\n\nQuestion:\n{query}"
    
    # 2) Generate answer using specified LLM provider
    try:
        logger.info(f"Generating answer using {llm_provider} with provided API key: {'Yes' if api_key else 'No'}")
        if llm_provider == "openai":
            response_text = call_openai(prompt, api_key=api_key)
        elif llm_provider == "gemini":
            response_text = call_gemini(prompt, api_key=api_key)
        else:
            return {"error": "Unsupported llm_provider. Use openai or gemini."}

        if not response_text:
            return {"error": "No response from LLM provider."}

        return {"response": response_text}
    except Exception as e:
        logger.error(f"Error during generation: {e}")
        return {"error": f"Generation failed: {str(e)}"}
