from fastapi import FastAPI, UploadFile, File, HTTPException
from app.utils.pdf_text import extract_pdf_text
from app.core.chunker import chunk_text
from app.core.embeddings import embed_chunks
from app.core.storage import save_index

app = FastAPI(title="RAG-Serve")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    try:
        content = await file.read()
        if file.filename.endswith(".pdf"):
            text = extract_pdf_text(content)
        else:
            text = content.decode("utf-8", errors="ignore")
        return {"status": "ingested", "length": len(text)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/index-doc")
async def index_doc(file: UploadFile = File(...)):
    content = await file.read()

    if file.filename.endswith(".pdf"):
        text = extract_pdf_text(content)
    else:
        text = content.decode("utf-8", errors="ignore")

    # 1. Chunk
    chunks = chunk_text(text)

    # 2. Embed
    embeddings = embed_chunks(chunks)

    # 3. Save
    save_index(chunks, embeddings)

    return {
        "chunks": len(chunks),
        "embedding_dim": len(embeddings[0]),
        "status": "indexed"
    }
