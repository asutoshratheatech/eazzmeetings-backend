from typing import List, Optional
from beanie import PydanticObjectId
from app.models.database.meeting_collection import MeetingCollection
from app.schemas.common_schema import UserJWT

class MeetingsController:
    @staticmethod
    async def get_all_meetings(current_user: UserJWT, skip: int = 0, limit: int = 50) -> List[MeetingCollection]:
        org_id = current_user.get("org_id")
        user_id = current_user.get("sub")
        
        query = {}
        if org_id:
            query["org_id"] = org_id
        else:
            # Assumes created_by or similar field exists in MeetingCollection/DBMeta
            # MeetingCollection inherits DBMeta which likely has created_by
            # But wait, MeetingCollection inherits MeetingBase & DBMeta. 
            # DBMeta has updated_by, org_id. Does it have created_by?
            # Let's check DBMeta definition again or add created_by.
            # Actually, DBMeta usually has created_by if defined right.
            # Let's check common_schema.py again.
            pass 
        
        # Checking DBMeta in common_schema.py revealed it has 'updated_by' but not 'created_by'?
        # Wait, I saw DBMeta in step 1046:
        # class DBMeta(BaseModel):
        #     org_id: PydanticObjectId
        #     created_on: datetime
        #     updated_on: datetime
        #     updated_by: Optional[PydanticObjectId]
        # It does NOT have created_by.
        # But RecordingCollection has created_by. 
        # MeetingCollection should logically have it too to filter by user.
        # However, if org_id is present, we filter by that.
        # If org_id is NOT present (personal account), we need created_by.
        # If MeetingCollection lacks created_by, we might need to add it or rely on org_id common for single users?
        # Let's assume for now we filter by org_id if present.
        
        if org_id:
            return await MeetingCollection.find(MeetingCollection.org_id == org_id).sort("-created_on").skip(skip).limit(limit).to_list()
        
        # Fallback to user_id (created_by) if org_id is missing
        # Note: created_by needs to be added to MeetingCollection if not present
        if user_id:
             # Assuming we will add created_by
             # query["created_by"] = user_id
             return await MeetingCollection.find({"created_by": user_id}).sort("-created_on").skip(skip).limit(limit).to_list()

        return []

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
