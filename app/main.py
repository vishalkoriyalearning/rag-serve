from fastapi import FastAPI, UploadFile, File, HTTPException
from app.utils.pdf_text import extract_pdf_text

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
