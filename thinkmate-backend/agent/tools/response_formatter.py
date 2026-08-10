"""
Response Formatter — generates the final, comprehensive explanation
once the guidance threshold is reached (Feature 3's "reveal" step),
grounded strictly in the retrieved document context.
"""
from core.llm_client import llm_client
from utils.prompt_loader import load_prompt

SYSTEM_PROMPT = load_prompt("final_explanation.txt")


def generate_final_explanation(student_query: str, context: str) -> str:
    prompt = f"""Study material context:
{context}

Student's original question: {student_query}

Provide the full explanation now."""

    return llm_client.generate(prompt, system=SYSTEM_PROMPT, temperature=0.3, max_tokens=400)
