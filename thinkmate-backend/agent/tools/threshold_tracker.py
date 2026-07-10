"""
Threshold-Based Learning (Feature 3 / the "novel feature" from the
Innovation section). Pure logic, no LLM call — deterministic and fast,
which also makes it trivially unit-testable.
"""
from config.settings import settings


def should_reveal_answer(guidance_step: int, threshold: int | None = None) -> bool:
    """True once the student has been through enough guidance steps."""
    limit = threshold if threshold is not None else settings.guidance_threshold
    return guidance_step >= limit


def next_hint_level(guidance_step: int, threshold: int | None = None) -> int:
    """
    Maps the current guidance step to a hint specificity level (1..3),
    scaling with however many steps are configured, so hints escalate
    smoothly regardless of the threshold value chosen.
    """
    limit = threshold if threshold is not None else settings.guidance_threshold
    ratio = guidance_step / max(limit, 1)
    if ratio < 0.4:
        return 1
    elif ratio < 0.75:
        return 2
    return 3
