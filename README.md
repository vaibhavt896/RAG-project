# Production RAG System

A production-grade Retrieval-Augmented Generation system with hybrid search, cross-encoder re-ranking, citation tracking, and an automated evaluation harness. Powered by **Google Gemini**.

## Architecture

```
User Query → Query Expansion → Hybrid Search (Vector + BM25) → RRF Fusion
→ Cross-Encoder Re-ranking → Citation Map → Gemini LLM → Cited Answer
→ Evaluation Harness (Faithfulness, Relevance, Recall, Precision)
```

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Google Gemini 1.5 Flash / Pro |
| Embeddings | Gemini text-embedding-004 |
| Vector DB | ChromaDB |
| Keyword Search | BM25s |
| Re-ranker | ms-marco-MiniLM-L-6-v2 |
| API | FastAPI |
| Observability | Langfuse |
| Frontend | Next.js |

## Quick Start

### 1. Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Fill in your API keys
```

### 2. Ingest Documents

```bash
python scripts/ingest.py --source data/raw/
```

### 3. Start API

```bash
uvicorn src.api.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### 4. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend at: http://localhost:3000

### 5. Run Evaluation

```bash
python scripts/evaluate.py --dataset data/eval/golden_dataset.json
```

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/ingest` | POST | Ingest a document (PDF, DOCX, TXT, URL) |
| `/query` | POST | Query with full RAG pipeline |
| `/health` | GET | Health check |
| `/stats` | GET | Index statistics |

## Key Features

- **Hybrid Search** — Vector (semantic) + BM25 (keyword) fused with Reciprocal Rank Fusion
- **Cross-Encoder Re-ranking** — Fine-grained scoring of (query, document) pairs
- **Citation Tracking** — Inline [1], [2] citations with source verification
- **Evaluation Harness** — Faithfulness, answer relevance, context recall/precision
- **Edge Case Handling** — Unanswerable detection, ambiguous queries, sensitive content filtering
- **Observability** — Langfuse tracing for every LLM call
