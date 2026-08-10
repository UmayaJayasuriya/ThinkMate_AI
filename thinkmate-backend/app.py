"""
ThinkMate AI — Backend Entrypoint

Wires together everything else in this codebase:
  - initializes the DB schema on startup
  - registers all routers (documents, qa, voice, progress)
  - exposes /health for a quick liveness check (useful for Docker healthchecks)

Run locally:
    uvicorn app:app --reload --host 0.0.0.0 --port 8000

Run in Docker: see Dockerfile / docker-compose.yml.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from core.database import init_db
from core.exceptions import register_exception_handlers
from routers import documents, qa, voice, progress
from utils.logger import setup_logging

setup_logging(debug=settings.debug)
logger = logging.getLogger("thinkmate.app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.app_name} ({settings.app_env})")
    init_db()
    logger.info("Database tables ensured.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title=settings.app_name,
    description="RAG + Agentic AI Socratic Learning Tutor — backend API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — open for hackathon dev; tighten allow_origins before any real deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(qa.router)
app.include_router(voice.router)
app.include_router(progress.router)

register_exception_handlers(app)


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}
