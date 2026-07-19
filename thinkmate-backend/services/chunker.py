"""
Text chunking. Using LangChain's RecursiveCharacterTextSplitter as the
"most accurate for now" default per your request — it splits on a
priority list of separators (paragraph -> sentence -> word) so chunks
break at natural boundaries instead of mid-sentence, which matters a
lot for embedding quality.

RESEARCH NOTE (alternatives to evaluate later):
- Fixed-size splitting (naive): fastest, worst quality — breaks
  sentences/ideas apart, hurts retrieval relevance.
- Semantic chunking (e.g. via embeddings similarity breakpoints,
  or `langchain_experimental.text_splitter.SemanticChunker`):
  groups by meaning rather than character count — better accuracy,
  but slower and needs an embedding call per chunk during splitting.
  Worth trying once graded on accuracy, not speed.
- Markdown/heading-aware splitting: if lecture notes have consistent
  heading structure, splitting on headings first preserves topic
  boundaries better than generic recursive splitting.
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config.settings import settings


def chunk_text(text: str, chunk_size: int | None = None, chunk_overlap: int | None = None) -> list[str]:
    """
    Split text into overlapping chunks. Overlap (default 120 chars)
    preserves context across chunk boundaries so a concept split
    across two chunks doesn't lose meaning in either one.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or settings.chunk_size,
        chunk_overlap=chunk_overlap or settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    chunks = splitter.split_text(text)
    # Drop near-empty chunks (e.g. page headers/footers that slipped through)
    return [c.strip() for c in chunks if len(c.strip()) > 20]
