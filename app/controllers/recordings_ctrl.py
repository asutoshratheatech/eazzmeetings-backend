"""
Controller for handling recording sessions and WebSocket logic.
"""
import os
import asyncio
from datetime import datetime
import json
import logging

from fastapi import WebSocket, WebSocketDisconnect, status, UploadFile

from app.services.storage import StorageService
from app.utils import convert_to_opus
from app.security import validate_jwt_token
from app.models.database.recordings_collection import RecordingCollection, RecordingStatus
from app.schemas.common_schema import UserJWT

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Storage Service
storage_service = StorageService()

async def handle_websocket_recording(websocket: WebSocket) -> None:
    """
    Handles the WebSocket recording session:
    1. Authenticates the user (10s timeout).
    2. Receives metadata (10s timeout).
    3. Creates DB Record (Status: RECORDING).
    4. Streams audio data to disk.
    5. Updates DB Record on completion/closure.
    """
    await websocket.accept()
    filename = ""
    recording_doc = None

    try:
        # --- STAGE 1: AUTHENTICATION (10s Timeout) ---
        try:
            auth_msg = await asyncio.wait_for(websocket.receive_json(), timeout=10.0)
        except asyncio.TimeoutError:
            logger.warning("Auth timeout")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Auth timeout")
            return

        token = auth_msg.get("token")
        if not token:
            logger.warning("No token provided")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="No token provided")
            return

        try:
            user_payload = validate_jwt_token(token)
        except ValueError as e:
            logger.warning(f"Token validation failed: {e}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
            return

        # Auth Success
        await websocket.send_json({"status": "authenticated"})
        logger.info(f"User authenticated: {user_payload.get('sub')}")

        # --- STAGE 2: METADATA (10s Timeout) ---
        try:
            metadata_msg = await asyncio.wait_for(websocket.receive_json(), timeout=10.0)
        except asyncio.TimeoutError:
            logger.warning("Metadata timeout")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Metadata timeout")
            return

        # Validate Metadata
        received_name = metadata_msg.get("name", "Unknown Meeting")
        meeting_link = metadata_msg.get("meeting_link")

        # Sanitize filename
        safe_name = "".join([c for c in received_name if c.isalpha() or c.isdigit() or c in " ._-"])
        date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_name}_{date_str}.raw"

        # --- CREATE DB RECORD ---
        # Note: We don't have the full path until we save, but for websocket stream we append.
        # StorageService abstracts the directory, but we might need the relative path or full path for DB.
        # For now, let's assume StorageService handles the base dir and we just need the filename.
        # But `file_path` in DB might expect full path or relative. The original code used full path joined with AUDIO_DIR.
        # Let's keep it consistent: StorageService.base_dir + filename
        file_path = os.path.join(storage_service.base_dir, filename)
        
        # Use auth token data for ownership
        user_id = user_payload.get("sub")
        # Check if org_id is in token payload, otherwise fallback to metadata
        org_id = user_payload.get("org_id") or metadata_msg.get("org_id")

        recording_doc = RecordingCollection(
            name=received_name,
            meeting_link=meeting_link,
            status=RecordingStatus.RECORDING,
            org_id=org_id,
            created_by=user_id,
            file_path=file_path
        )
        await recording_doc.create() # Save to DB

        # Metadata Success
        await websocket.send_json({"status": "recording_started", "filename": filename})
        logger.info(f"Recording started. DB ID: {recording_doc.id}, Filename: {filename}")

        # --- STAGE 3: CONTINUOUS STREAM LOOP ---
        # We don't need to ensure dir here as StorageService does it on init or write
        
        while True:
            # Wait for next chunk (Audio Bytes or JSON Control Message)
            message = await websocket.receive()

            if "bytes" in message:
                await storage_service.append_file(filename, message["bytes"])
            elif "text" in message:
                # Handle Control Messages
                try:
                    text_data = json.loads(message["text"])
                    if text_data.get("type") == "stop_recording":
                        logger.info("Received stop_recording signal.")
                        recording_doc.status = RecordingStatus.COMPLETE
                        await recording_doc.save()
                        await websocket.close()
                        return # Clean exit
                except json.JSONDecodeError:
                    pass # Ignore non-JSON text
                
                pass

    except WebSocketDisconnect:
        logger.info(f"Client disconnected. Saved: {filename}")
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(f"Error: {e}")
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except Exception: # pylint: disable=broad-exception-caught
            pass
    finally:
        # Final Status Update if needed
        if recording_doc:
            # Re-fetch to ensure we have latest state if concurrent edits happened (unlikely here but safe)
            # Actually, we just check local state or assume if not COMPLETE, it's FORCED
            if recording_doc.status == RecordingStatus.RECORDING:
                recording_doc.status = RecordingStatus.COMPLETE_FORCED
                await recording_doc.save()
                logger.warning(f"Recording {recording_doc.id} marked as COMPLETE_FORCED due to unexpected closure.")


async def stream_audio_chunk(session_id: str, chunk_index: int, input_bytes: bytes) -> dict:
    """
    Processes a single audio chunk: uploads to storage and returns status.
    """
    # 2. Convert to Opus
    # Note: Appending OGG pages blindly works for chained OGG streams.
    opus_bytes = convert_to_opus(input_bytes)

    # 3. Append to file
    filename = f"{session_id}.ogg"
    
    await storage_service.append_file(filename, opus_bytes)

    return {
        "status": "success",
        "session_id": session_id,
        "chunk_index": chunk_index,
        "size_appended": len(opus_bytes)
    }

async def upload_audio_file(file: UploadFile, current_user: UserJWT) -> dict:
    """
    Processes a full audio file upload.
    """
    input_bytes = await file.read()
    if not input_bytes:
        raise ValueError("Empty file")

    # Convert to Opus
    opus_bytes = convert_to_opus(input_bytes)

    # Determine filename
    original_name = file.filename or "uploaded_file"
    safe_name = "".join([c for c in original_name if c.isalpha() or c.isdigit() or c in " ._-"])
    base_name = os.path.splitext(safe_name)[0]
    filename = f"{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ogg"

    file_path = await storage_service.save_file(filename, opus_bytes)

    # Create DB Record
    user_id = current_user.get("sub")
    org_id = current_user.get("org_id")

    recording_doc = RecordingCollection(
        name=base_name,
        status=RecordingStatus.COMPLETE,
        org_id=org_id,
        created_by=user_id,
        file_path=file_path
    )
    await recording_doc.create()

    return {
        "status": "success",
        "filename": filename,
        "size": len(opus_bytes),
        "recording_id": str(recording_doc.id)
    }

