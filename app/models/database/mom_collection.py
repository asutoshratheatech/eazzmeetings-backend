from datetime import datetime
from typing import List, Optional
from beanie import Document
from pydantic import Field

class MoMCollection(Document):
    recording_id: str  # Link to the RecordingCollection (string ID)
    summary: str
    action_items: List[str] = []
    key_decisions: List[str] = []
    sentiment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "minutes_of_meeting"
