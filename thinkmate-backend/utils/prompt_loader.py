"""
Loads system prompts from the prompts/ directory. Centralizing this
means non-Python teammates can tune tutor behavior by editing a .txt
file — no need to touch agent tool code. Cached so files are only read
from disk once per process.
"""
import os
from functools import lru_cache

PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")


@lru_cache(maxsize=None)
def load_prompt(filename: str) -> str:
    path = os.path.join(PROMPTS_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()
