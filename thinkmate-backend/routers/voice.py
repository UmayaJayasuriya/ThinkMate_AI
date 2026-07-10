"""
POST /voice-input — Phase-4 priority per the build order. Transcribes
uploaded audio to text; frontend then feeds that text into /ask-question
as a normal query, so no agent logic duplication is needed here.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException

from models.schemas import VoiceInputResponse
from services.stt_service import transcribe_audio

router = APIRouter(tags=["voice"])

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".webm"}


@router.post("/voice-input", response_model=VoiceInputResponse)
async def voice_input(file: UploadFile = File(...)):
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported audio format: {ext}")

    audio_bytes = await file.read()
    text = transcribe_audio(audio_bytes, suffix=ext)

    if not text:
        raise HTTPException(422, "Could not transcribe audio — try again or use text input.")

    return VoiceInputResponse(transcribed_text=text)
