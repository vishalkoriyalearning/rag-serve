![CI](https://github.com/vishalkoriyalearning/rag-serve/actions/workflows/ci.yml/badge.svg)
# 🚀 RAG-Serve — Retrieval Augmented Generation API

**RAG-Serve** is a production-ready, containerized **RAG (Retrieval-Augmented Generation)** system built with **FastAPI**, **FAISS**, **Sentence-Transformers**, and **LLMs (OpenAI + Ollama fallback)**.

It ingests documents → chunks them → builds embeddings → stores a FAISS vector index → retrieves relevant context → and generates answers using LLMs.

This project demonstrates:

* Backend/API engineering
* RAG pipeline architecture
* Hybrid LLM usage (Cloud + Local)
* FAISS vector search
* Docker & CI/CD
* Test-driven workflow

---

## 📦 Features

* **Document Ingestion** (`/ingest`, `/index-doc`)
* **Text Extraction** from PDF & TXT
* **Chunking** with overlap
* **Embeddings** using `sentence-transformers`
* **FAISS Vector Store** for fast retrieval
* **Query API** for semantic search
* **Generate API** using:

  * **OpenAI (Primary)**
  * **Ollama Llama3.2:1b (Fallback)**
* **Dockerized Deployment** (API + Ollama)
* **GitHub Actions CI**

  * Linting (Ruff)
  * Unit tests (PyTest)
  * Docker build
* **Simple, clean architecture**

---

## 🧱 Tech Stack

* **FastAPI** — API framework
* **FAISS** — vector similarity search
* **Sentence-Transformers** — embedding generation
* **OpenAI GPT models** — generation (optional)
* **Ollama Llama3.2:1b** — local generation fallback
* **Docker + Docker Compose**
* **GitHub Actions (CI)**
* **PyTest + Ruff**

---

## 📂 Project Structure

```
rag-serve/
├─ app/
│  ├─ api/
│  ├─ core/         # chunker, embeddings, vectorstore, generator
│  ├─ utils/        # pdf text extraction
│  └─ main.py       # FastAPI root
├─ configs/         # model configs
├─ storage/         # FAISS + metadata
├─ tests/           # pytest unit tests
├─ docker-compose.yml
├─ Dockerfile
└─ README.md
```

---

## 🚀 Getting Started (Local)

### 1. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run FastAPI

```bash
uvicorn app.main:app --reload
```

Visit → [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🐳 Run with Docker (Recommended)

### 1. Build + start services (API + Ollama)

```bash
docker-compose up --build
```

### 2. Pull Ollama model (inside container)

```bash
docker exec -it ollama ollama pull llama3.2:1b
```

---

## 🧪 Testing

Run all unit tests:

```bash
pytest -q
```

Lint the code:

```bash
ruff check .
```

---

## 🔌 API Endpoints

### ✔ Health Check

`GET /health`

### ✔ Ingest Document

`POST /ingest`

### ✔ Build Index

`POST /index-doc`

### ✔ Semantic Search

`POST /query`

### ✔ RAG + LLM Answer

`POST /generate`
Uses **OpenAI → fallback to Ollama**

---

## 🔄 CI/CD (GitHub Actions)

* Automatic linting
* Automatic tests
* Automatic Docker build
* Status badge included in this repo

---

## 📘 Notes

This project is built as a **learning-by-doing** portfolio system to demonstrate knowledge of:

* AI engineering
* Modern backend design
* Vector search
* LLM integrations
* Dockerized microservices
* CI/CD automation

It is structured to be easily extended with:

* Reranking
* Chat memory
* UI client
* API authentication
* MLflow experiment tracking

