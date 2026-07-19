"""
Centralized configuration. Everything that could change between dev/
hackathon-demo/production lives here — never hardcode this stuff in
services or routers.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    app_name: str = "ThinkMate AI Backend"
    app_env: str = "development"
    debug: bool = True
    guidance_threshold: int = 3  # Feature 3: guidance steps before answer reveal

    # PostgreSQL
    database_url: str = "postgresql+psycopg2://thinkmate:thinkmate_pass@localhost:5432/thinkmate_db"

    # ChromaDB
    chroma_persist_dir: str = "./chroma_data"
    chroma_collection_name: str = "thinkmate_documents"

    # LLM
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    llm_provider: str = "ollama"  # swap to "huggingface" later without touching callers
    llm_timeout_seconds: int = 60

    # Embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Uploads
    upload_dir: str = "./uploads"
    max_upload_mb: int = 25

    # Chunking
    chunk_size: int = 800
    chunk_overlap: int = 120

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Singleton — import `settings` everywhere, never re-instantiate Settings()
settings = Settings()
