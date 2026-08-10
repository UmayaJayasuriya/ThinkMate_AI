"""
Practice Question Generation (Feature 9) — generates a follow-up
question after a concept has been explained, to reinforce learning
in a slightly different context/scenario.
"""
from core.llm_client import llm_client
from utils.prompt_loader import load_prompt

SYSTEM_PROMPT = load_prompt("practice_question.txt")


def generate_practice_question(explained_concept: str, context: str) -> str:
    prompt = f"""Study material context:
{context}

Concept just explained to the student: {explained_concept}

Generate one practice question applying this concept in a new scenario."""

    return llm_client.generate(prompt, system=SYSTEM_PROMPT, temperature=0.7)
