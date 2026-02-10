from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from beanie import PydanticObjectId
from app.models.database.recordings_collection import RecordingStatus

class RecordingOut(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    name: str
    meeting_link: Optional[str] = None
    status: RecordingStatus
    creation_date: datetime
    org_id: Optional[str] = None
    file_path: str

    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            PydanticObjectId: str
        }

class RecordingStats(BaseModel):
    total_meetings: int
    open_tasks: int # Mocked for now or fetched from another collection
    intelligence_count: int # Mocked
