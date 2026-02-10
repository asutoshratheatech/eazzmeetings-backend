
from typing import List, Optional
from beanie import PydanticObjectId
from app.models.database.meeting_collection import MeetingCollection

class MeetingsController:
    @staticmethod
    async def get_all_meetings(skip: int = 0, limit: int = 50) -> List[MeetingCollection]:
        return await MeetingCollection.find_all().skip(skip).limit(limit).to_list()

    @staticmethod
    async def get_meeting(meeting_id: PydanticObjectId) -> Optional[MeetingCollection]:
        return await MeetingCollection.get(meeting_id)

    @staticmethod
    async def generate_html(meeting_id: PydanticObjectId) -> Optional[str]:
        meeting = await MeetingCollection.get(meeting_id)
        if not meeting:
            return None
        
        from jinja2 import Environment, FileSystemLoader
        import os
        from datetime import datetime
        
        template_dir = os.path.join(os.getcwd(), "app", "templates")
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("mom.html")
        
        return template.render(
            meeting=meeting,
            current_date=datetime.now().strftime("%Y-%m-%d")
        )
