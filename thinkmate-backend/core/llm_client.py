"""
LLM client abstraction. All agent tools call `llm_client.generate(...)`
and never talk to Ollama/HuggingFace directly — this is the one file
you touch to swap providers (e.g. move to a cloud-hosted vLLM endpoint
in Phase 3, per the scalability plan).
"""
import json
import logging

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import settings

logger = logging.getLogger("thinkmate.llm_client")


class LLMClient:
    """Provider-agnostic interface. `provider` picks the backend."""

    def __init__(self, provider: str | None = None):
        self.provider = provider or settings.llm_provider

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    def generate(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.4,
        max_tokens: int = 512,
    ) -> str:
        if self.provider == "ollama":
            return self._generate_ollama(prompt, system, temperature, max_tokens)
        elif self.provider == "huggingface":
            return self._generate_huggingface(prompt, system, temperature, max_tokens)
        raise ValueError(f"Unknown LLM provider: {self.provider}")

    def _generate_ollama(self, prompt, system, temperature, max_tokens) -> str:
        payload = {
            "model": settings.ollama_model,
            "prompt": prompt,
            "system": system or "",
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        resp = requests.post(
            f"{settings.ollama_host}/api/generate",
            json=payload,
            timeout=settings.llm_timeout_seconds,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "").strip()

    def _generate_huggingface(self, prompt, system, temperature, max_tokens) -> str:
        """
        Placeholder for a future local HuggingFace `transformers` pipeline
        or Inference Endpoint call. Kept here so switching providers is a
        config change (LLM_PROVIDER=huggingface), not a rewrite.
        """
        raise NotImplementedError(
            "HuggingFace provider not wired yet — implement when moving off Ollama."
        )

    def generate_json(self, prompt: str, system: str | None = None) -> dict:
        """
        Convenience wrapper for tools that need structured output
        (e.g. AnswerEvaluator). Strips markdown fences defensively since
        local models often ignore 'JSON only' instructions.
        """
        raw = self.generate(prompt, system=system, temperature=0.2)
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("LLM did not return valid JSON, returning raw text wrapped")
            return {"raw": raw}


llm_client = LLMClient()
