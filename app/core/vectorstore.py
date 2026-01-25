import faiss
import numpy as np
import os
import json

EMBEDDING_DIM = 384  # MiniLM-L6-v2
FAISS_INDEX_FILE = "app/storage/faiss.index"
CHUNKS_FILE = "app/storage/chunks.json"


def build_faiss_index(embeddings: np.ndarray):
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index


def save_faiss_index(index):
    faiss.write_index(index, FAISS_INDEX_FILE)


def load_faiss_index():
    if not os.path.exists(FAISS_INDEX_FILE):
        return None
    return faiss.read_index(FAISS_INDEX_FILE)


def save_chunks(chunks: list[str]):
    with open(CHUNKS_FILE, "w") as f:
        json.dump(chunks, f)


def load_chunks():
    if not os.path.exists(CHUNKS_FILE):
        return []
    with open(CHUNKS_FILE, "r") as f:
        return json.load(f)
