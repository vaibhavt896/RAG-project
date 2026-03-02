<div align="center">

# 🧠 Production RAG System

**A production-grade Retrieval-Augmented Generation system with hybrid search, cross-encoder re-ranking, citation tracking, and an automated evaluation harness.**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org)
[![Gemini](https://img.shields.io/badge/Powered%20by-Google%20Gemini-4285F4?style=flat-square&logo=google&logoColor=white)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

[**Live Demo**](https://rag-project-liard.vercel.app) · [**API Docs**](https://rag-project-wp25.onrender.com/docs) · [**Report Bug**](https://github.com/vaibhavt896/RAG-project/issues)

</div>

---

## ✨ What Makes This Different

Most RAG demos are a single `embed → query → answer` call. This system is a **full production pipeline**:

| Stage | What Happens |
|---|---|
| **Query Expansion** | Rewrites the user query to improve recall |
| **Hybrid Search** | Vector (semantic) + BM25 (keyword) in parallel |
| **RRF Fusion** | Reciprocal Rank Fusion merges both result sets |
| **Cross-Encoder Re-ranking** | `ms-marco-MiniLM-L-6-v2` scores every (query, chunk) pair |
| **Citation Mapping** | Every sentence is traced back to its source chunk |
| **LLM Generation** | Gemini generates a grounded, cited answer |
| **Observability** | Every LLM call is traced in Langfuse |
| **Evaluation** | Automated faithfulness, relevance, recall, and precision scoring |

---

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Query                           │
└───────────────────────────┬─────────────────────────────────┘
                            │
                    Query Expansion
                            │
              ┌─────────────┴─────────────┐
              │                           │
       Vector Search               BM25 Keyword Search
       (ChromaDB)                  (BM25s)
              │                           │
              └─────────────┬─────────────┘
                            │
                     RRF Fusion
                            │
               Cross-Encoder Re-ranking
               (ms-marco-MiniLM-L-6-v2)
                            │
                   Citation Mapping
                            │
               Gemini LLM Generation
                            │
                 ┌──────────┴──────────┐
                 │                     │
           Cited Answer          Evaluation Harness
                                (Faithfulness, Relevance,
                                 Recall, Precision)
```

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| LLM | Google Gemini 1.5 Flash / Pro |
| Embeddings | `text-embedding-004` (Gemini) |
| Vector DB | ChromaDB |
| Keyword Search | BM25s |
| Re-ranker | `ms-marco-MiniLM-L-6-v2` (cross-encoder) |
| API | FastAPI |
| Observability | Langfuse |
| Frontend | Next.js 14 |
| Containerization | Docker + Docker Compose |

---

## 💬 Sample Output

```
Query: "What were Infosys's key financial highlights for FY2024?"

Answer:
Infosys reported revenues of $18.56 billion for FY2024, representing a
year-over-year growth of 1.4% in constant currency [1]. Operating margins
improved to 20.7%, driven by cost optimization initiatives and higher
utilization rates [2]. The company returned $1.6 billion to shareholders
through dividends and buybacks [3].

Sources:
[1] Infosys Annual Report 2024, p.12 — Revenue Overview
[2] Infosys Annual Report 2024, p.34 — Operating Performance
[3] Infosys Annual Report 2024, p.67 — Capital Allocation
```

---

## 📊 Evaluation Results

Evaluated on a golden dataset of 50 question-answer pairs across financial documents:

| Metric | Score |
|---|---|
| **Faithfulness** | 0.91 |
| **Answer Relevance** | 0.88 |
| **Context Recall** | 0.84 |
| **Context Precision** | 0.79 |

> Evaluation framework: custom harness in `src/evaluation/` using Gemini as the judge model.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Google Gemini API key ([get one free](https://ai.google.dev))

### 1. Clone & Setup

```bash
git clone https://github.com/vaibhavt896/RAG-project.git
cd RAG-project

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # Then fill in your API keys
```

### 2. Ingest Documents

```bash
python scripts/ingest.py --source data/raw/
```

Supports **PDF, DOCX, TXT, and URLs** out of the box.

### 3. Start the API

```bash
uvicorn src.api.main:app --reload --port 8000
```

Interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: [http://localhost:3000](http://localhost:3000)

### 5. Run Evaluation

```bash
python scripts/evaluate.py --dataset data/eval/golden_dataset.json
```

### 6. Docker (Full Stack)

```bash
docker-compose up --build
```

---

## 🌐 Deploy for Free

### Frontend → Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/vaibhavt896/RAG-project&root=frontend)

1. Click the button above
2. Set environment variable: `NEXT_PUBLIC_API_URL=https://your-render-url.onrender.com`
3. Deploy — Vercel auto-deploys on every push to `main`

### Backend → Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/vaibhavt896/RAG-project)

1. Click the button above
2. Set all environment variables from `.env.example` in the Render dashboard
3. Deploy — Render will use the included `Dockerfile`

---

## 📡 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/ingest` | `POST` | Ingest a document (PDF, DOCX, TXT, URL) |
| `/query` | `POST` | Query the full RAG pipeline |
| `/health` | `GET` | Health check |
| `/stats` | `GET` | Index and retrieval statistics |

Full interactive docs at `/docs` when the server is running.

---

## 🔑 Environment Variables

Copy `.env.example` to `.env` and fill in the values:

| Variable | Description | Where to get it |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini API key | [ai.google.dev](https://ai.google.dev) — Free |
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key | [cloud.langfuse.com](https://cloud.langfuse.com) — Free |
| `LANGFUSE_SECRET_KEY` | Langfuse secret key | Same as above |

> ⚠️ **Never commit your `.env` file.** It is included in `.gitignore` by default.

---

## 🔒 Security

- All API keys are loaded via environment variables — never hardcoded
- `.env` is gitignored and was never committed to this repository
- The `.env.example` file contains only placeholder values
- Sensitive content filtering is built into the retrieval pipeline (`src/retrieval/edge_cases.py`)

---

## 📁 Project Structure

```
RAG-project/
├── src/
│   ├── api/            # FastAPI app, routes, schemas
│   ├── ingestion/      # Document loading and chunking
│   ├── retrieval/      # Vector, BM25, hybrid search, re-ranking
│   ├── generation/     # LLM calls and prompt templates
│   ├── citation/       # Citation tracking and validation
│   ├── evaluation/     # Evaluation harness and metrics
│   └── observability/  # Langfuse tracing
├── frontend/           # Next.js 14 frontend
├── scripts/            # CLI scripts (ingest, evaluate)
├── data/
│   ├── raw/            # Source documents
│   └── eval/           # Golden evaluation dataset
├── Dockerfile
├── docker-compose.yml
└── render.yaml         # Render deployment config
```

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first.

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.
