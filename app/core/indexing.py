from __future__ import annotations

from uuid import uuid4
from fastapi import BackgroundTasks

from app.core.chunker import chunk_text
from app.core.embeddings import embed_chunks
from app.core.vectorstore import build_faiss_index, save_faiss_index, save_chunks
from app.utils.logging import get_logger
from app.utils.pdf_text import extract_pdf_text

logger = get_logger()

index_jobs: dict[str, dict] = {}


def _index_document_task(filename: str, content: bytes, job_id: str) -> None:
    try:
        logger.info(f"Index-doc background job started. job_id={job_id}, file={filename}")
        if filename.endswith(".pdf"):
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
        logger.info(
            "Chunks embedded. Embedding dimension: "
            f"{embeddings.shape[1] if hasattr(embeddings, 'shape') else 'unknown'}."
        )

        logger.info("Building FAISS index.")
        index = build_faiss_index(embeddings)

        logger.info("Saving FAISS index and chunks metadata.")
        save_faiss_index(index)
        save_chunks(chunks)

        index_jobs[job_id] = {
            "status": "completed",
            "chunks_indexed": len(chunks),
            "embedding_dim": embeddings.shape[1] if hasattr(embeddings, "shape") else None,
            "faiss_saved": True,
        }
        logger.info(f"Indexing complete. job_id={job_id}")
    except Exception as e:
        logger.error(f"Index-doc background job failed. job_id={job_id} error={e}")
        index_jobs[job_id] = {"status": "failed", "error": str(e)}


def start_index_job(background_tasks: BackgroundTasks, filename: str, content: bytes) -> str:
    job_id = str(uuid4())
    index_jobs[job_id] = {"status": "queued", "file": filename}
    background_tasks.add_task(_index_document_task, filename, content, job_id)
    return job_id


def get_index_job(job_id: str) -> dict | None:
    return index_jobs.get(job_id)
