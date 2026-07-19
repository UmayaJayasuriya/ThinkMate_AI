"""
Agentic AI Controller (Feature 8) — implements the Plan-Act-Observe-
Reflect loop from the architecture diagram. This is a hand-rolled state
machine, not LangGraph — deliberately simpler so it's easy to debug
under hackathon time pressure. Swap in LangGraph later if you want
more complex branching without much rework, since each tool call below
is already a standalone function.

Flow per turn:
  PLAN     -> decide which tool to invoke based on session state
  ACT      -> call that tool
  OBSERVE  -> capture the result
  REFLECT  -> update session state (guidance_step, weak topics) for next turn
"""
import logging

from sqlalchemy.orm import Session

from agent.tools import (
    question_generator,
    answer_evaluator,
    hint_generator,
    threshold_tracker,
    weak_topic_analyzer,
    practice_generator,
    response_formatter,
)
from models.db_models import ChatSession, Message
from services.retriever import retrieve_relevant_chunks, format_context_for_prompt

logger = logging.getLogger("thinkmate.agent")


def start_or_continue_session(db: Session, session: ChatSession, student_query: str) -> dict:
    """
    PLAN + ACT for a fresh question. If this is a new topic (no prior
    guidance steps), ask the first Socratic question. Grounds everything
    in retrieved context from the student's own document.
    """
    chunks = retrieve_relevant_chunks(student_query, document_id=session.document_id)
    context = format_context_for_prompt(chunks)

    question = question_generator.generate_question(student_query, context)

    session.topic = session.topic or student_query[:200]
    session.guidance_step_count = 1
    session.last_question = question
    session.last_context = context
    db.add(Message(session_id=session.id, role="student", content=student_query, message_type="query"))
    db.add(Message(session_id=session.id, role="tutor", content=question, message_type="question"))
    db.commit()

    return {
        "action": "question",
        "content": question,
        "guidance_step": session.guidance_step_count,
    }


def process_student_answer(db: Session, session: ChatSession, student_answer: str) -> dict:
    """
    PLAN -> ACT -> OBSERVE -> REFLECT for one round-trip after the
    student submits an answer to a guiding question or hint.
    Reads last_question/last_context from the session row so the API
    stays stateless between requests.
    """
    last_question = session.last_question or ""
    context = session.last_context or ""

    # ACT: evaluate the answer
    evaluation = answer_evaluator.evaluate_answer(student_answer, last_question, context)
    classification = evaluation["classification"]

    # REFLECT: log to weak-topic tracking regardless of what happens next
    weak_topic_analyzer.record_evaluation(db, session.user_id, session.topic, classification)

    db.add(Message(session_id=session.id, role="student", content=student_answer, message_type="answer"))

    # PLAN: decide next action
    if classification == "correct":
        practice_q = practice_generator.generate_practice_question(session.topic, context)
        db.add(Message(session_id=session.id, role="tutor", content=practice_q, message_type="practice"))
        db.commit()
        return {
            "evaluation": classification,
            "feedback": evaluation["feedback"],
            "next_action": "practice",
            "content": practice_q,
            "guidance_step": session.guidance_step_count,
        }

    # Not correct yet — check threshold before deciding hint vs. reveal
    session.guidance_step_count += 1
    reveal = threshold_tracker.should_reveal_answer(session.guidance_step_count)

    if reveal:
        explanation = response_formatter.generate_final_explanation(session.topic, context)
        db.add(Message(session_id=session.id, role="tutor", content=explanation, message_type="explanation"))
        db.commit()
        return {
            "evaluation": classification,
            "feedback": evaluation["feedback"],
            "next_action": "explanation",
            "content": explanation,
            "guidance_step": session.guidance_step_count,
        }

    hint_level = threshold_tracker.next_hint_level(session.guidance_step_count)
    hint = hint_generator.generate_hint(student_answer, last_question, context, hint_level)
    session.last_question = hint  # student now responds relative to the hint
    db.add(Message(session_id=session.id, role="tutor", content=hint, message_type="hint"))
    db.commit()

    return {
        "evaluation": classification,
        "feedback": evaluation["feedback"],
        "next_action": "hint",
        "content": hint,
        "guidance_step": session.guidance_step_count,
    }
