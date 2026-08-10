"""
Custom exceptions so callers get clean, specific error responses
instead of generic 500s. Register `register_exception_handlers(app)`
once in app.py.
"""
from fastapi import Request
from fastapi.responses import JSONResponse


class ThinkMateError(Exception):
    """Base class for all ThinkMate domain errors."""
    status_code = 500

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class DocumentProcessingError(ThinkMateError):
    """Raised when PDF parsing/chunking/embedding fails."""
    status_code = 422


class SessionNotFoundError(ThinkMateError):
    status_code = 404


class LLMProviderError(ThinkMateError):
    """Raised when Ollama/HuggingFace call fails after retries."""
    status_code = 502


def register_exception_handlers(app):
    @app.exception_handler(ThinkMateError)
    async def handle_thinkmate_error(request: Request, exc: ThinkMateError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.__class__.__name__, "message": exc.message},
        )
