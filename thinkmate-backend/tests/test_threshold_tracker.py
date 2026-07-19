"""
Unit tests for threshold_tracker.py — pure logic, no DB/LLM required,
so this is the fastest test in the suite and a good first thing to run.
Run with: pytest tests/test_threshold_tracker.py -v
"""
from agent.tools.threshold_tracker import should_reveal_answer, next_hint_level


def test_reveal_triggers_exactly_at_threshold():
    assert should_reveal_answer(guidance_step=2, threshold=3) is False
    assert should_reveal_answer(guidance_step=3, threshold=3) is True
    assert should_reveal_answer(guidance_step=5, threshold=3) is True


def test_hint_level_escalates():
    levels = [next_hint_level(step, threshold=3) for step in (1, 2, 3)]
    assert levels == [1, 2, 3]


def test_hint_level_scales_with_custom_threshold():
    # With a threshold of 6, step 2 should still be an early/subtle hint
    assert next_hint_level(1, threshold=6) == 1
    assert next_hint_level(6, threshold=6) == 3
