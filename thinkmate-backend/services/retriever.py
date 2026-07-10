"""
Retrieval service — the glue between embedder.py and core/vectorstore.py.
This is the function the Agent's RAG Retriever tool calls; test this
standalone (see tests/test_retrieval.py) before wiring it to the agent,
so retrieval bugs don't get buried under agent/LLM complexity.
"""
import logging

from core.vectorstore import vector_store
from services.embedder import embed_query

logger = logging.getLogger("thinkmate.retriever")


def retrieve_relevant_chunks(query: str, document_id: str, top_k: int = 5) -> list[dict]:
    """
    Returns top-k relevant chunks for a query, scoped to one document
    (so tutoring stays grounded in *that student's* uploaded material,
    not other students' documents).
    """
    query_embedding = embed_query(query)
    results = vector_store.query(query_embedding, top_k=top_k, document_id=document_id)

    chunks = []
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for doc, meta, dist in zip(documents, metadatas, distances):
        chunks.append({
            "text": doc,
            "chunk_index": meta.get("chunk_index"),
            "similarity_score": 1 - dist,  # cosine distance -> similarity
        })

    logger.info(f"Retrieved {len(chunks)} chunks for query: '{query[:50]}...'")
    return chunks


def format_context_for_prompt(chunks: list[dict]) -> str:
    """Join retrieved chunks into a single context block for the LLM prompt."""
    if not chunks:
        return "No relevant material found in the uploaded document."
    return "\n\n---\n\n".join(c["text"] for c in chunks)
