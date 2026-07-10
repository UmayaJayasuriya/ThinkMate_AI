"""
Embedding generation via Sentence-Transformers (all-MiniLM-L6-v2) —
the accurate-enough, fast, CPU-friendly default per the tech stack.

RESEARCH NOTE (alternatives to evaluate later):
- all-mpnet-base-v2: noticeably higher retrieval accuracy than MiniLM,
  but ~3x slower and larger — good upgrade if judges care about answer
  quality over latency and you have GPU access.
- BAAI/bge-small-en-v1.5 or bge-base: strong open models tuned
  specifically for retrieval (asymmetric query/passage embedding),
  often outperform generic sentence-transformers models on RAG
  benchmarks. Worth an A/B test if time allows.
- OpenAI text-embedding-3-small: highest quality but requires an API
  key/cost and breaks the "fully local, no API costs" pitch in your
  proposal — avoid unless you drop that requirement.

The model loads once at import time (singleton) — loading it per
request would add multi-second latency to every call.
"""
import logging

from sentence_transformers import SentenceTransformer

from config.settings import settings

logger = logging.getLogger("thinkmate.embedder")

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of chunks. Batching is much faster than looping one-by-one."""
    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    """Embed a single query string for retrieval."""
    model = _get_model()
    embedding = model.encode([query], show_progress_bar=False, normalize_embeddings=True)
    return embedding[0].tolist()
