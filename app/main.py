from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RAG-Serve")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from app.utils.pdf_text import extract_pdf_text

from app.core.chunker import chunk_text
from app.core.embeddings import embed_chunks

from app.core.vectorstore import (
    build_faiss_index,
    save_faiss_index,
    save_chunks
)

from pydantic import BaseModel
from app.core.search import search, generate_answer

from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import PlainTextResponse
from time import time

from app.utils.logging import get_logger


logger = get_logger()



logger.info("Starting RAG-Serve FastAPI application.")

@app.get("/health")
def health():
    logger.debug("Health check endpoint called.")
    return {"status": "ok"}


requests_total = Counter("requests_total", "Total API requests", ["endpoint"])
latency_hist = Histogram("request_latency_seconds", "API latency", ["endpoint"])

@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest(), media_type="text/plain")

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    logger.info(f"Ingest endpoint called with file: {file.filename}")
    try:
        content = await file.read()
        logger.debug(f"Read {len(content)} bytes from file: {file.filename}")
        if file.filename.endswith(".pdf"):
            logger.debug("Extracting text from PDF file.")
            text = extract_pdf_text(content)
        else:
            logger.debug("Decoding text from non-PDF file.")
            text = content.decode("utf-8", errors="ignore")
        logger.info(f"File ingested successfully. Length: {len(text)} characters.")
        return {"status": "ingested", "length": len(text)}
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/index-doc")
async def index_doc(file: UploadFile = File(...)):
    logger.info(f"Index-doc endpoint called with file: {file.filename}")
    content = await file.read()
    logger.debug(f"Read {len(content)} bytes from file: {file.filename}")

    if file.filename.endswith(".pdf"):
        logger.debug("Extracting text from PDF file.")
        text = extract_pdf_text(content)
    else:
        logger.debug("Decoding text from non-PDF file.")
        text = content.decode("utf-8", errors="ignore")

    logger.info("Chunking text.")
    chunks = chunk_text(text)
    logger.info(f"Text chunked into {len(chunks)} chunks.")

    logger.info("Embedding chunks.")
    embeddings = embed_chunks(chunks)
    logger.info(f"Chunks embedded. Embedding dimension: {embeddings.shape[1] if hasattr(embeddings, 'shape') else 'unknown'}.")

    logger.info("Building FAISS index.")
    index = build_faiss_index(embeddings)

    logger.info("Saving FAISS index and chunks metadata.")
    save_faiss_index(index)
    save_chunks(chunks)

    logger.info("Indexing complete.")
    return {
        "chunks_indexed": len(chunks),
        "embedding_dim": embeddings.shape[1],
        "faiss_saved": True
    }

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

@app.post("/query")
def query_text(req: QueryRequest):
    logger.info(f"Query endpoint called. Query: {req.query}, top_k: {req.top_k}")
    result = search(req.query, req.top_k)
    logger.debug(f"Query result: {result}")
    return result

class GenRequest(BaseModel):
    query: str
    top_k: int = 5

@app.post("/generate")
def generate_api(req: GenRequest, x_api_key: str = Header(None)):
    start = time()
    requests_total.labels(endpoint="/generate").inc()
    logger.info(f"Generate endpoint called. Query: {req.query}, top_k: {req.top_k}")
    result = generate_answer(req.query, req.top_k, api_key=x_api_key)
    logger.debug(f"Generated answer: {result}")
    latency_hist.labels(endpoint="/generate").observe(time() - start)
    return result