"""
Text-to-speech. Lowest priority per your build order — proposal lists
Piper TTS OR Browser Web Speech API as options.

Recommendation: skip a backend TTS service entirely for the MVP and
use the Browser's built-in Web Speech API (`speechSynthesis`) on the
frontend instead — zero backend cost, zero extra dependency, works
offline in-browser. Only build this server-side service if you need
TTS in contexts without a browser (e.g. a future mobile app in Phase 4).

Left as a stub so the interface exists if/when you do need it.
"""


def synthesize_speech(text: str) -> bytes:
    """
    Placeholder for Piper TTS integration. Not implemented — the MVP
    should use the browser's Web Speech API on the frontend instead.
    """
    raise NotImplementedError(
        "Server-side TTS not implemented for MVP. Use browser speechSynthesis() "
        "on the frontend, or implement Piper TTS here if a backend voice is required."
    )
