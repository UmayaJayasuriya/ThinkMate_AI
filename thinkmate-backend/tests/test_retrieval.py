"""
Standalone retrieval test — this is Step 9 from the original build
order: verify RAG retrieval works BEFORE trusting the agent layer on
top of it. Requires a real ChromaDB instance with at least one
document already uploaded via /upload-document.

Run with: pytest tests/test_retrieval.py -v -s
(the -s flag shows the print output so you can eyeball result quality)
"""
import pytest

from services.retriever import retrieve_relevant_chunks


@pytest.mark.integration
def test_retrieval_returns_relevant_chunks():
    """
    Replace DOCUMENT_ID with a real one from an /upload-document
    response before running. This test is intentionally manual/visual —
    automated relevance scoring is out of scope for a hackathon MVP.
    """
    document_id = "REPLACE_WITH_REAL_DOCUMENT_ID"
    query = "What is the main topic of this document?"

    chunks = retrieve_relevant_chunks(query, document_id=document_id, top_k=3)

    assert isinstance(chunks, list)
    for chunk in chunks:
        print(f"\n[score={chunk['similarity_score']:.3f}] {chunk['text'][:150]}...")
