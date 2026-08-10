"""
Core tutoring endpoints: POST /ask-question, POST /submit-answer.
These are thin — all real logic lives in agent/agent_controller.py.
Routers should stay thin like this; keeps business logic testable
without spinning up FastAPI.
"""
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from agent import agent_controller
from config.settings import settings
from core.database import get_db
from core.exceptions import SessionNotFoundError
from models.db_models import ChatSession
from models.schemas import (
    AskQuestionRequest, AskQuestionResponse,
    SubmitAnswerRequest, SubmitAnswerResponse,
)

router = APIRouter(tags=["qa"])


@router.post("/ask-question", response_model=AskQuestionResponse)
def ask_question(payload: AskQuestionRequest, db: Session = Depends(get_db)):
    if payload.session_id:
        session = db.query(ChatSession).filter_by(id=payload.session_id).first()
        if not session:
            raise SessionNotFoundError(f"Session {payload.session_id} not found.")
    else:
        session = ChatSession(
            id=str(uuid.uuid4()),
            user_id=payload.user_id,
            document_id=payload.document_id,
        )
        db.add(session)
        db.commit()

    result = agent_controller.start_or_continue_session(db, session, payload.query)

    return AskQuestionResponse(
        session_id=session.id,
        action=result["action"],
        content=result["content"],
        guidance_step=result["guidance_step"],
        threshold=settings.guidance_threshold,
    )


@router.post("/submit-answer", response_model=SubmitAnswerResponse)
def submit_answer(payload: SubmitAnswerRequest, db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter_by(id=payload.session_id).first()
    if not session:
        raise SessionNotFoundError(f"Session {payload.session_id} not found.")

    result = agent_controller.process_student_answer(db, session, payload.student_answer)

    return SubmitAnswerResponse(
        evaluation=result["evaluation"],
        feedback=result["feedback"],
        next_action=result["next_action"],
        content=result["content"],
        guidance_step=result["guidance_step"],
    )
