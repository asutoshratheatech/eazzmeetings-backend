"""
Database model for Recording sessions.
"""
from datetime import datetime
from typing import Optional
from enum import Enum
from beanie import Document
from pydantic import Field

class RecordingStatus(str, Enum):
    """
    Status of the recording session.
    """
    RECORDING = "recording"
    COMPLETE = "complete"
    COMPLETE_FORCED = "complete_forced"
    ARCHIVED = "archived"
    EXPIRED = "expired"

class RecordingCollection(Document):
    """
    Collection for storing recording metadata and status.
    """
    name: str
    meeting_link: Optional[str] = None
    status: RecordingStatus = Field(default=RecordingStatus.RECORDING)
    org_id: Optional[str] = None
    created_by: str  # Storing User ID as string for simplicity, or could use Link[UserCollection]
    creation_date: datetime = Field(default_factory=datetime.utcnow)
    file_path: str
    
    class Settings:
        """
        Beanie settings.
        """
        name = "recordings"
