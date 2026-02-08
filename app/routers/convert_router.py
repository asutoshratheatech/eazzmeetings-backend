
from fastapi import APIRouter, File, UploadFile, Depends, Response
from app.controllers.convert_ctrl import convert_to_flac_ctrl, convert_to_opus_ctrl
from app.security import get_current_user
from app.schemas.common_schema import UserJWT

router = APIRouter()

@router.post("/convert/flac")
async def convert_to_flac(
    file: UploadFile = File(...),
    current_user: UserJWT = Depends(get_current_user)
):
    """
    Authenticated endpoint to convert audio to FLAC.
    """
    flac_bytes = await convert_to_flac_ctrl(file)
    return Response(content=flac_bytes, media_type="audio/flac")

@router.post("/convert/opus")
async def convert_to_opus(
    file: UploadFile = File(...),
    current_user: UserJWT = Depends(get_current_user)
):
    """
    Authenticated endpoint to convert audio to Opus (OGG).
    """
    opus_bytes = await convert_to_opus_ctrl(file)
    return Response(content=opus_bytes, media_type="audio/ogg")
