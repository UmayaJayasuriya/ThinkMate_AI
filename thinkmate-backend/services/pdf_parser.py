"""
PDF text extraction. PyMuPDF (fitz) chosen as the accurate default per
the tech stack — it's fast and handles most digitally-generated PDFs
(lecture slides exported to PDF, typed notes) well.

RESEARCH NOTE (alternatives, for later comparison):
- pdfplumber: better at preserving table layout, slower than PyMuPDF.
- pdfminer.six: lower-level, more control, more code to maintain.
- Tesseract OCR (pytesseract): required for SCANNED/image-only PDFs —
  PyMuPDF returns empty/garbled text on these. Marked Phase-2 "if time
  permits" in the proposal; add as a fallback when `extract_text`
  returns near-empty content (see `is_likely_scanned` below).
"""
import logging

import fitz  # PyMuPDF

logger = logging.getLogger("thinkmate.pdf_parser")


def extract_text(file_path: str) -> str:
    """Extract raw text from a PDF, page by page."""
    text_parts = []
    with fitz.open(file_path) as doc:
        for page_num, page in enumerate(doc):
            page_text = page.get_text("text")
            text_parts.append(page_text)
    full_text = "\n".join(text_parts)
    logger.info(f"Extracted {len(full_text)} chars from {file_path}")
    return full_text


def is_likely_scanned(text: str, min_chars_per_page: int = 20, page_count: int = 1) -> bool:
    """
    Heuristic: if extracted text is suspiciously short relative to page
    count, this is probably a scanned/image PDF and needs OCR instead.
    Use this to decide whether to route to Tesseract in Phase 2.
    """
    return len(text.strip()) < (min_chars_per_page * max(page_count, 1))


def get_page_count(file_path: str) -> int:
    with fitz.open(file_path) as doc:
        return doc.page_count
