from app.core.search import generate_answer

def test_generate_answer():
    resp = generate_answer("Hello test query", top_k=2)
    assert "response" in resp
