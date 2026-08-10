"""
Progressive hint system (Feature 5). Hints get more specific as
guidance_step increases, so a struggling student gets more scaffolding
without immediately being handed the answer.
"""
from core.llm_client import llm_client
from utils.prompt_loader import load_prompt

SYSTEM_PROMPT = load_prompt("hint.txt")


def generate_hint(student_answer: str, guiding_question: str, context: str, hint_level: int) -> str:
    prompt = f"""Study material context:
{context}

Guiding question: {guiding_question}
Student's attempt: {student_answer}
Hint level: {hint_level} (1=subtle nudge, 2=more specific direction, 3=near-explicit clue)

Generate a hint at this level. Do not state the final answer."""

    return llm_client.generate(prompt, system=SYSTEM_PROMPT, temperature=0.5)
