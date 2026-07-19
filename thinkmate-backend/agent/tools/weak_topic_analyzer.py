"""
Weak Topic Tracking (Feature 6). Pure DB logic — updates struggle
scores based on evaluation outcomes, no LLM call needed.
"""
from datetime import datetime

from sqlalchemy.orm import Session

from models.db_models import WeakTopic, StudentProgress

STRUGGLE_WEIGHT = {
    "incorrect": 1.0,
    "incomplete": 0.6,
    "partially_correct": 0.3,
    "correct": -0.5,  # improving on a topic reduces its struggle score
}


def record_evaluation(db: Session, user_id: str, topic: str, classification: str):
    """Update both StudentProgress counters and the WeakTopic struggle score."""
    progress = db.query(StudentProgress).filter_by(user_id=user_id, topic=topic).first()
    if not progress:
        progress = StudentProgress(user_id=user_id, topic=topic)
        db.add(progress)

    if classification == "correct":
        progress.correct_count += 1
    elif classification == "partially_correct":
        progress.partial_count += 1
    else:
        progress.incorrect_count += 1
    progress.last_updated = datetime.utcnow()

    weight = STRUGGLE_WEIGHT.get(classification, 0.0)
    weak = db.query(WeakTopic).filter_by(user_id=user_id, topic=topic).first()
    if not weak:
        weak = WeakTopic(user_id=user_id, topic=topic, struggle_score=max(weight, 0))
        db.add(weak)
    else:
        weak.struggle_score = max(0.0, weak.struggle_score + weight)
        weak.times_flagged += 1
        weak.last_flagged_at = datetime.utcnow()
        weak.resolved = weak.struggle_score <= 0

    db.commit()
