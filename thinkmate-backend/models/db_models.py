"""
ORM models — mirrors the PostgreSQL block in the system architecture
diagram: users, chat_sessions, student_progress, weak_topics.
`messages` added underneath chat_sessions since chat history needs
row-level storage, not just a session record.
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Text, Integer, Float, ForeignKey, DateTime, Boolean
)
from sqlalchemy.orm import relationship

from core.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("ChatSession", back_populates="user")
    progress = relationship("StudentProgress", back_populates="user")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    chunk_count = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    document_id = Column(String, ForeignKey("documents.id"), nullable=True)
    topic = Column(String, nullable=True)
    guidance_step_count = Column(Integer, default=0)  # feeds ThresholdTracker
    last_question = Column(Text, nullable=True)  # persisted so /submit-answer can reference it
    last_context = Column(Text, nullable=True)   # retrieved chunks, cached to avoid re-embedding
    started_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=gen_uuid)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # student | tutor
    message_type = Column(String, default="text")  # question|hint|evaluation|answer|practice
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")


class StudentProgress(Base):
    __tablename__ = "student_progress"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    topic = Column(String, nullable=False)
    correct_count = Column(Integer, default=0)
    incorrect_count = Column(Integer, default=0)
    partial_count = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="progress")


class WeakTopic(Base):
    __tablename__ = "weak_topics"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    topic = Column(String, nullable=False)
    struggle_score = Column(Float, default=0.0)  # higher = weaker
    times_flagged = Column(Integer, default=1)
    resolved = Column(Boolean, default=False)
    last_flagged_at = Column(DateTime, default=datetime.utcnow)
