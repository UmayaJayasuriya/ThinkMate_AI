"""
POST /upload-document — the entry point to the whole pipeline:
save file -> extract text -> chunk -> embed -> store in ChromaDB ->
record in Postgres. Test this endpoint standalone before anything
downstream depends on it.
"""
import logging
import os
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from config.settings import settings
from core.database import get_db
from core.exceptions import DocumentProcessingError
from core.vectorstore import vector_store
from models.db_models import Document
from models.schemas import DocumentUploadResponse
from services.chunker import chunk_text
from services.embedder import embed_texts
from services.pdf_parser import extract_text, is_likely_scanned, get_page_count

logger = logging.getLogger("thinkmate.documents")
router = APIRouter(tags=["documents"])

os.makedirs(settings.upload_dir, exist_ok=True)


@router.post("/upload-document", response_model=DocumentUploadResponse)
async def upload_document(
    user_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported currently.")

    contents = await file.read()
    if len(contents) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(400, f"File exceeds {settings.max_upload_mb}MB limit.")

    document_id = str(uuid.uuid4())
    saved_path = os.path.join(settings.upload_dir, f"{document_id}.pdf")
    with open(saved_path, "wb") as f:
        f.write(contents)

    # --- Step 6: extract text ---
    text = extract_text(saved_path)
    page_count = get_page_count(saved_path)

    if is_likely_scanned(text, page_count=page_count):
        logger.warning(f"{file.filename} looks scanned — OCR not implemented yet, proceeding with sparse text.")

    if not text.strip():
        raise DocumentProcessingError("Could not extract any text from this PDF.")

    # --- Step 7: chunk ---
    chunks = chunk_text(text)
    if not chunks:
        raise DocumentProcessingError("Document produced no usable chunks after processing.")

    # --- Step 8: embed + store in ChromaDB ---
    embeddings = embed_texts(chunks)
    vector_store.add_chunks(chunks, embeddings, document_id=document_id, metadata_extra={"filename": file.filename})

    # --- record in Postgres ---
    doc_record = Document(
        id=document_id,
        user_id=user_id,
        filename=file.filename,
        chunk_count=len(chunks),
    )
    db.add(doc_record)
    db.commit()

    return DocumentUploadResponse(document_id=document_id, filename=file.filename, chunk_count=len(chunks))
