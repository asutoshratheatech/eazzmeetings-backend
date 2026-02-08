
import logging
from fastapi import UploadFile, HTTPException
from app.services.transcribers import TranscriptionService, ModelChoices
from app.schemas.media_schema import TranscribeResponse

logger = logging.getLogger(__name__)

# Initialize the service - could be dependency injected but simple init for now
transcription_service = TranscriptionService()

async def transcribe_audio_ctrl(file: UploadFile, model: ModelChoices = ModelChoices.WHISPER_LARGE) -> TranscribeResponse:
    """
    Controller logic to transcribe an audio file using Groq/Whisper.
    """
    try:
        # Read the file content
        file_content = await file.read()
        if not file_content:
            raise HTTPException(status_code=400, detail="Empty file")

        # Call the service
        # Note: The service expects bytes and returns a dict
        filename = file.filename or "audio.wav"
        logger.info(f"Transcribing {filename} with model: {model} (type: {type(model)})")
        result_dict = transcription_service.whisper_transcribe(file_content, filename, model.value)

        # Map to schema
        return TranscribeResponse(
            text=result_dict.get("text", ""),
            segments=result_dict.get("segments", []),
            language=result_dict.get("language"),
            duration=result_dict.get("duration")
        )

    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
