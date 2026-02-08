"""
Router for audio recordings, handling streaming and upload endpoints.
"""
import logging

from fastapi import APIRouter, WebSocket, UploadFile, File, Form, HTTPException, Depends

from app.controllers.recordings_ctrl import (
    handle_websocket_recording,
    stream_audio_chunk as ctrl_stream_audio_chunk,
    upload_audio_file as ctrl_upload_audio_file
)
from app.security import get_current_user
from app.schemas.common_schema import UserJWT

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()
logger.info("Loading Recordings Router...")

@router.websocket("/ws/record")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for recording audio.
    Delegates logic to the controller.
    """
    await handle_websocket_recording(websocket)


@router.post("/recordings/stream")
async def stream_audio_chunk_endpoint(
    file: UploadFile = File(...),
    session_id: str = Form(...),
    chunk_index: int = Form(...)
):
    """
    Receives a chunk of audio (e.g., mp4a, wav), converts it to 1s Opus (24kbps/16kHz),
    and appends it to the session file.
    """
    try:
        # 1. Read input bytes
        input_bytes = await file.read()
        if not input_bytes:
            raise HTTPException(status_code=400, detail="Empty file chunk")

        # 2. Delegate to controller
        return await ctrl_stream_audio_chunk(session_id, chunk_index, input_bytes)

    except Exception as e:
        logger.error("Error processing chunk: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/recordings/upload")
async def upload_audio_file_endpoint(
    file: UploadFile = File(...),
    current_user: UserJWT = Depends(get_current_user)
):
    """
    Receives a full audio file, converts it to Opus (24kbps/16kHz), and saves it.
    Authenticated endpoint. Creates a DB record.
    """
    try:
        # Delegate to controller
        return await ctrl_upload_audio_file(file, current_user)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error("Error uploading file: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e
