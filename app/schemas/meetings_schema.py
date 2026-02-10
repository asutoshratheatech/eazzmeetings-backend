"""
A collection of meeting records.
"""
from pydantic import HttpUrl
from pydantic import BaseModel
from app.schemas import (
                        GeneralSummaries,
                        TopicSummaries,
                        Decisions,
                        ActionItems,
                        Facts,
                        Attendees
                        )
from typing import Optional
from beanie import PydanticObjectId

class MeetingBase(BaseModel):
    """
        The root model containing all extraction categories.
    """
    transcription: str
    meeting_link: str
    audio_url: str
    
    general_summaries: GeneralSummaries
    topic_summaries: TopicSummaries
    decisions: Decisions

    action_items: ActionItems
    facts: Facts
    attendees: Attendees

    meeting_date: str
    meeting_time: str
    meeting_duration: str
    
    recording_id: Optional[PydanticObjectId] = None

