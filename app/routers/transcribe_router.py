
from fastapi import APIRouter, File, UploadFile, Depends
from app.controllers.transcribe_ctrl import transcribe_audio_ctrl
from app.security import get_current_user
from app.schemas.common_schema import UserJWT
from app.schemas.media_schema import TranscribeResponse
from app.services.transcribers import ModelChoices

router = APIRouter()

@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    model: ModelChoices = ModelChoices.WHISPER_LARGE,
    current_user: UserJWT = Depends(get_current_user)
):
    """
    Authenticated endpoint to transcribe audio.
    """
    return await transcribe_audio_ctrl(file, model)
