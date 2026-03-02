# LinkedIn Intelligence Agent

Signal-first LinkedIn automation with 7 specialized AI agents, Gemini-powered personalization, ChromaDB vector storage, and a real-time Next.js dashboard. **100% free stack. Zero paid services.**

## Quick Start

### 1. Copy and fill in your keys

```bash
cp .env.example .env
# Edit .env with your Gemini API key, LinkedIn creds, email finder keys, etc.
```

### 2. Run backend locally

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Start FastAPI
uvicorn app.main:app --reload
# → http://localhost:8000/docs
```

### 3. Run frontend locally

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### 4. Start services (Docker)

```bash
# Start PostgreSQL + Redis
docker compose up postgres redis -d

# Run migrations
cd backend && alembic upgrade head
```

### 5. Start Celery workers

```bash
cd backend

# Worker
celery -A app.celery_app worker --loglevel=info

# Beat scheduler (separate terminal)
celery -A app.celery_app beat --loglevel=info
```

---

## Free Tier API Keys

| Service | Free Quota | URL |
|---|---|---|
| Gemini 1.5 Flash | 1,500 req/day | https://aistudio.google.com |
| Apollo.io | 50 lookups/mo | https://apollo.io |
| Hunter.io | 25 lookups/mo | https://hunter.io |
| Skrapp.io | 150 lookups/mo | https://skrapp.io |
| Gmail SMTP | 500 emails/day | myaccount.google.com → App Passwords |

---

## Project Structure

```
backend/app/
├── agents/          # 7 Celery agents (signal, scraper, ai_writer, outreach, safety, analytics, learning)
├── api/             # 6 FastAPI routers
├── core/            # Behavior engine, health scorer, embeddings, ChromaDB, context assembler
├── models/          # SQLAlchemy models
├── schemas/         # Pydantic schemas
└── services/        # LinkedIn scraper, email finder, funding signals, Gemini, Gmail

frontend/
├── app/             # Next.js 15 pages (dashboard, campaigns, companies, leads, analytics)
└── components/      # HealthMeter, ActivityFeed, SignalRadar, Sidebar
```

---

## 21-Day Outreach Sequence

```
Day 0  → Like their most recent post
Day 2  → Follow their company
Day 4  → Comment on their post (Gemini-written)
Day 6  → Connection request (no note = higher acceptance)
Day 9  → Message 1 (only if connected)
Day 14 → Message 2 (only if no reply, different angle)
Day 21 → Email (only if email found + no LinkedIn reply)
```

**Hard stop:** Reply received → automation immediately pauses → you take over.

---

## Safety Rules

- **Never** log into LinkedIn to collect data (public scraper only)
- **Never** run outside 9AM–6PM in the user's timezone
- **Never** use constant delays (always `HumanBehaviorEngine.wait()`)
- **Hard stop** on any CAPTCHA — log and alert
- Health score < 50 → all activity pauses automatically
