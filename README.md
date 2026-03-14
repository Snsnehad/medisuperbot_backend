# MediSuperBot API
**Compatible with Python 3.11 & 3.12 (Anaconda)**

---

## Quick Start (First Time)

### Step 1 — Create environment
```bash
conda create -n medisuperbot python=3.11 -y
conda activate medisuperbot
```

### Step 2 — Install packages
```bash
pip install -r requirements.txt
```

### Step 3 — Add your API keys
Copy `.env.example` to `.env` and fill in:
```
GOOGLE_API_KEY=AIza...
GROQ_API_KEY=gsk_...
PINECONE_API_KEY=pcsk_...
PINECONE_INDEX_NAME=medical-index
```

### Step 4 — Run
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Open: http://localhost:8000/docs

---

## Pinned Versions (Why)

| Package | Version | Reason |
|---|---|---|
| google-genai | 1.12.1 | Latest that works on Python 3.11/3.12 |
| langchain-google-genai | 2.1.12 | Compatible with google-genai 1.12.1 |
| pinecone | 5.4.2 | Stable, no breaking changes |
| fastapi | 0.115.0 | LTS stable release |

---

## API Endpoints

| Method | URL | Description |
|---|---|---|
| GET | / | Health check |
| POST | /upload_pdfs/ | Upload PDFs (form-data, key: files) |
| POST | /ask/ | Ask question (form-data, key: question) |

---

## Pinecone Index
- dimension: **3072** (text-embedding-004 output size)
- metric: **cosine**
- cloud: **aws / us-east-1**

If you already have an old index with dimension=768, delete it from
app.pinecone.io and restart the server — it will recreate it at 3072.
