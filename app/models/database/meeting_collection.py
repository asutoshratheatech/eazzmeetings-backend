"""
Meeting Collection Model
"""

from typing import Optional
from beanie import Document, PydanticObjectId
from app.schemas import (
                        MeetingBase,
                        DBMeta
                    )

class MeetingCollection(Document,MeetingBase,DBMeta):
    """
    Meeting Collection Model
    """
    created_by: Optional[PydanticObjectId] = None

    class Settings:
        """
        Beanie settings.
        """
        name = "meetings"