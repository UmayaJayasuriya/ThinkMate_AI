"""
ChromaDB wrapper. Uses a PersistentClient so embeddings survive
container restarts (a common hackathon gotcha — the in-memory client
looks fine in dev then silently loses everything on redeploy).
"""
import uuid
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from config.settings import settings


class VectorStore:
    def __init__(self):
        self._client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(
        self,
        chunks: list[str],
        embeddings: list[list[float]],
        document_id: str,
        metadata_extra: dict[str, Any] | None = None,
    ) -> list[str]:
        """Store chunk embeddings tagged with document_id for later filtering."""
        ids = [f"{document_id}_{uuid.uuid4().hex[:8]}" for _ in chunks]
        metadatas = [
            {"document_id": document_id, "chunk_index": i, **(metadata_extra or {})}
            for i in range(len(chunks))
        ]
        self._collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
        )
        return ids

    def query(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        document_id: str | None = None,
    ) -> dict:
        """Semantic search. Optionally restrict to one document (per-student material)."""
        where = {"document_id": document_id} if document_id else None
        return self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
        )

    def delete_document(self, document_id: str):
        self._collection.delete(where={"document_id": document_id})


# Singleton — instantiated once, reused across requests
vector_store = VectorStore()
