"""
Pydantic schemas for request/response validation. Keep these separate
from db_models.py (ORM) — mixing the two leads to leaking internal
fields (like guidance_step_count) straight into API responses.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ---------- Documents ----------

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    chunk_count: int
    message: str = "Document processed and indexed successfully."


# ---------- Q&A / Agent ----------

class AskQuestionRequest(BaseModel):
    user_id: str
    document_id: str
    session_id: str | None = None
    query: str = Field(..., description="Student's question or topic to explore")


class AskQuestionResponse(BaseModel):
    session_id: str
    action: Literal["question", "hint", "explanation"]
    content: str
    guidance_step: int
    threshold: int


class SubmitAnswerRequest(BaseModel):
    session_id: str
    user_id: str
    student_answer: str


class SubmitAnswerResponse(BaseModel):
    evaluation: Literal["correct", "partially_correct", "incorrect", "incomplete"]
    feedback: str
    next_action: Literal["question", "hint", "explanation", "practice"]
    content: str
    guidance_step: int


class VoiceInputResponse(BaseModel):
    transcribed_text: str


# ---------- Progress ----------

class TopicProgress(BaseModel):
    topic: str
    correct_count: int
    incorrect_count: int
    partial_count: int
    last_updated: datetime


class ProgressResponse(BaseModel):
    user_id: str
    topics: list[TopicProgress]


class WeakTopicItem(BaseModel):
    topic: str
    struggle_score: float
    times_flagged: int
    last_flagged_at: datetime


class WeakTopicsResponse(BaseModel):
    user_id: str
    weak_topics: list[WeakTopicItem]
