import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from server.middlewares.exception_handlers import catch_exception_middleware
from server.routes.upload_pdfs import router as upload_router
from server.routes.ask_question import router as ask_router

app = FastAPI(
    title="MediSuperBot API",
    description="RAG-powered medical document Q&A backend",
    version="1.0.0",
)

# ── CORS ───────────────────────────────────────────────────────────────────────
# In production set ALLOWED_ORIGINS env variable to your frontend URL
# e.g.  ALLOWED_ORIGINS=https://your-app.vercel.app
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
origins = [o.strip() for o in allowed_origins_env.split(",")] if allowed_origins_env != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(BaseHTTPMiddleware, dispatch=catch_exception_middleware)

# ── Routes ─────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "MediSuperBot API"}


app.include_router(upload_router, tags=["Documents"])
app.include_router(ask_router,    tags=["Q&A"])
