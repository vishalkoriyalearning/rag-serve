from app.core.chunker import chunk_text

def test_chunking():
    text = " ".join(["hello"] * 1000)
    chunks = chunk_text(text)
    assert len(chunks) > 0
    assert isinstance(chunks[0], str)
