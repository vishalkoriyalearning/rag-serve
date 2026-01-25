from sentence_transformers import SentenceTransformer

_model = None

def get_embedding_model(name: str = "all-MiniLM-L6-v2"): # default model, can be changed to OpenAI's embedding  model if needed.
    global _model
    if _model is None:
        _model = SentenceTransformer(name)
    return _model

def embed_chunks(chunks: list[str]):
    model = get_embedding_model()
    embeddings = model.encode(
        chunks,
        show_progress_bar=False,
        convert_to_numpy=True
    )
    return embeddings
