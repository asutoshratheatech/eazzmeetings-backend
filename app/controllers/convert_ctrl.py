
import logging
from fastapi import UploadFile, HTTPException
from app.utils import convert, convert_to_opus

logger = logging.getLogger(__name__)

async def convert_to_flac_ctrl(file: UploadFile) -> bytes:
    """
    Controller logic to convert an audio file to FLAC format.
    """
    try:
        # We need a filename for the convert function, though distinct from the file object
        filename = file.filename or "temp_audio"
        flac_data = await convert(file, filename)
        return flac_data
    except Exception as e:
        logger.error(f"Error converting to FLAC: {e}")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

async def convert_to_opus_ctrl(file: UploadFile) -> bytes:
    """
    Controller logic to convert an audio file to Opus (OGG) format.
    """
    try:
        input_bytes = await file.read()
        if not input_bytes:
            raise HTTPException(status_code=400, detail="Empty file")
            
        opus_data = convert_to_opus(input_bytes)
        return opus_data
    except Exception as e:
        logger.error(f"Error converting to Opus: {e}")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")
