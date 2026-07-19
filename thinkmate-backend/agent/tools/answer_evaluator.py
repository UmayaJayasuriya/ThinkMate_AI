"""
Evaluates a student's answer against the retrieved context, classifying
it as correct / partially_correct / incorrect / incomplete, per
Feature 4. Returns structured JSON so the agent controller can branch
on it deterministically rather than parsing free text.
"""
from core.llm_client import llm_client
from utils.prompt_loader import load_prompt

SYSTEM_PROMPT = load_prompt("evaluate_answer.txt")


def evaluate_answer(student_answer: str, guiding_question: str, context: str) -> dict:
    prompt = f"""Study material context:
{context}

Guiding question asked: {guiding_question}
Student's answer: {student_answer}

Evaluate the student's answer."""

    result = llm_client.generate_json(prompt, system=SYSTEM_PROMPT)

    # Defensive default if the model returned malformed JSON
    if "classification" not in result:
        result = {
            "classification": "incomplete",
            "feedback": "Could not confidently evaluate — let's try another angle.",
            "misconception": None,
        }
    return result
