from pydantic import BaseModel
from typing import List, Optional, Any

class TranscribeResponse(BaseModel):
    text: str
    segments: List[Any] # You can define a more specific segment schema if needed, but Any/dict is fine for now as it comes from Whisper/Groq
    language: Optional[str] = None
    duration: Optional[float] = None
    # Add other fields as returned by the transcription service

class ConvertResponse(BaseModel):
    filename: str
    media_type: str
    size: int
