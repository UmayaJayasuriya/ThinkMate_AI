"""
GET /get-progress, GET /weak-topics — feeds the Progress Dashboard
(Presentation Layer, Feature 6). Pure read endpoints, no LLM calls.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from models.db_models import StudentProgress, WeakTopic
from models.schemas import (
    ProgressResponse, TopicProgress,
    WeakTopicsResponse, WeakTopicItem,
)

router = APIRouter(tags=["progress"])


@router.get("/get-progress", response_model=ProgressResponse)
def get_progress(user_id: str, db: Session = Depends(get_db)):
    rows = db.query(StudentProgress).filter_by(user_id=user_id).all()
    topics = [
        TopicProgress(
            topic=r.topic,
            correct_count=r.correct_count,
            incorrect_count=r.incorrect_count,
            partial_count=r.partial_count,
            last_updated=r.last_updated,
        )
        for r in rows
    ]
    return ProgressResponse(user_id=user_id, topics=topics)


@router.get("/weak-topics", response_model=WeakTopicsResponse)
def get_weak_topics(user_id: str, db: Session = Depends(get_db)):
    rows = (
        db.query(WeakTopic)
        .filter_by(user_id=user_id, resolved=False)
        .order_by(WeakTopic.struggle_score.desc())
        .all()
    )
    weak_topics = [
        WeakTopicItem(
            topic=r.topic,
            struggle_score=r.struggle_score,
            times_flagged=r.times_flagged,
            last_flagged_at=r.last_flagged_at,
        )
        for r in rows
    ]
    return WeakTopicsResponse(user_id=user_id, weak_topics=weak_topics)
