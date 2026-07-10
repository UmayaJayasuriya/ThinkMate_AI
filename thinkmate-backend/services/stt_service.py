"""
Speech-to-text via OpenAI Whisper (local, open-source model — not the
paid API). Phase-4-priority per your build order; scaffolded now so
the /voice-input endpoint has something real to call once you get to it.

RESEARCH NOTE: `whisper` "base" model is a reasonable CPU-speed/accuracy
tradeoff for a demo. "small"/"medium" are more accurate but slower —
only worth it if you have GPU access during the hackathon.
"""
import logging
import tempfile

import whisper

logger = logging.getLogger("thinkmate.stt_service")

_model = None


def _get_model():
    global _model
    if _model is None:
        logger.info("Loading Whisper model: base")
        _model = whisper.load_model("base")
    return _model


def transcribe_audio(audio_bytes: bytes, suffix: str = ".wav") -> str:
    """Transcribe raw audio bytes (from an uploaded voice recording) to text."""
    model = _get_model()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        result = model.transcribe(tmp.name)
    return result.get("text", "").strip()
