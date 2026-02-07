from fastapi import FastAPI, UploadFile, File, HTTPException, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.utils.pdf_text import extract_pdf_text
from pydantic import BaseModel
from app.core.search import search, generate_answer
from app.core.indexing import start_index_job, get_index_job
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import PlainTextResponse
from time import time
from app.utils.logging import get_logger


app = FastAPI(title="RAG-Serve")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vishalkoriyalearning.github.io",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/index-doc", status_code=202)
async def index_doc(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    logger.info(f"Index-doc endpoint called with file: {file.filename}")
    content = await file.read()
    logger.debug(f"Read {len(content)} bytes from file: {file.filename}")
    job_id = start_index_job(background_tasks, file.filename, content)

    return {
        "status": "queued",
        "job_id": job_id,
        "message": "Indexing started in background. Check /index-status/{job_id} for progress."
    }

@app.get("/index-status/{job_id}")
def index_status(job_id: str):
    job = get_index_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job ID not found.")
    return job

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
def generate_api(req: GenRequest, llm_provider: str, x_api_key: str = Header(None)):
    start = time()
    requests_total.labels(endpoint="/generate").inc()
    logger.info(f"Generate endpoint called. Query: {req.query}, top_k: {req.top_k}")
    result = generate_answer(req.query, req.top_k, llm_provider, api_key=x_api_key)
    logger.debug(f"Generated answer: {result}")
    latency_hist.labels(endpoint="/generate").observe(time() - start)
    return result
