from app.core.embeddings import embed_chunks

def test_embeddings_shape():
    x = embed_chunks(["hello world"])
    assert x.shape[1] > 0
