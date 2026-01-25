import json
import os

INDEX_FILE = "app\storage\index.json"

def save_index(chunks, embeddings):
    data = []
    for i, chunk in enumerate(chunks):
        data.append({
            "id": i,
            "text": chunk,
            "embedding": embeddings[i].tolist()
        })

    with open(INDEX_FILE, "w") as f:
        json.dump(data, f)

def load_index():
    if not os.path.exists(INDEX_FILE):
        return []
    with open(INDEX_FILE, "r") as f:
        return json.load(f)
