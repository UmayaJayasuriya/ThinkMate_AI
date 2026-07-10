"""
Generates a Socratic guiding question grounded in retrieved document
context — never a direct answer. This is Feature 2 from the proposal.
"""
from core.llm_client import llm_client
from utils.prompt_loader import load_prompt

SYSTEM_PROMPT = load_prompt("socratic_question.txt")


def generate_question(student_query: str, context: str) -> str:
    prompt = f"""Study material context:
{context}

Student's question: {student_query}

Generate one Socratic guiding question (not the answer) to help the
student reason toward understanding this themselves."""

    return llm_client.generate(prompt, system=SYSTEM_PROMPT, temperature=0.6)
