from __future__ import annotations

import os

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

from app.utils.logging import get_logger

load_dotenv()

logger = get_logger()

_local_model = None
_openai_client = None


def _platform() -> str:
    return os.getenv("PLATFORM", "LOCAL").upper()


def _get_local_embedding_model():
    # Lazy import to avoid pulling in torch on CLOUD deployments.
    from sentence_transformers import SentenceTransformer

    global _local_model
    if _local_model is None:
        model_name = os.getenv("LOCAL_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        logger.info(f"Loading local embedding model: {model_name}")
        _local_model = SentenceTransformer(model_name)
    return _local_model


def _get_openai_client(api_key: str | None = None) -> OpenAI:
    global _openai_client
    if api_key:
        return OpenAI(api_key=api_key)
    if _openai_client is None:
        _openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _openai_client


def embed_chunks(chunks: list[str]):
    """Embed a list of text chunks into vectors.

    PLATFORM=LOCAL: sentence-transformers (local embeddings)
    PLATFORM=CLOUD: OpenAI embeddings API (remote embeddings)
    """
    if not chunks:
        return np.zeros((0, 0), dtype="float32")

    plat = _platform()
    if plat == "CLOUD":
        model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        logger.info(f"Embedding via OpenAI. model={model} items={len(chunks)}")
        client = _get_openai_client()
        resp = client.embeddings.create(model=model, input=chunks)
        vectors = [item.embedding for item in resp.data]
        return np.array(vectors, dtype="float32")

    # Default: LOCAL
    model = _get_local_embedding_model()
    embeddings = model.encode(chunks, show_progress_bar=False, convert_to_numpy=True)
    # Ensure FAISS-friendly dtype
    return np.asarray(embeddings, dtype="float32")
