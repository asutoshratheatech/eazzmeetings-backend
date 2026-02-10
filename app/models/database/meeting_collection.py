"""
Meeting Collection Model
"""

from beanie import Document
from app.schemas import (
                        MeetingBase,
                        DBMeta
                    )

class MeetingCollection(Document,MeetingBase,DBMeta):
    """
    Meeting Collection Model
    """
    class Settings:
        """
        Beanie settings.
        """
        name = "meetings"