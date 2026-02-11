
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from beanie import PydanticObjectId

from app.controllers.meetings_ctrl import MeetingsController
from app.models.database.meeting_collection import MeetingCollection
from app.security import get_current_user
from app.schemas.common_schema import UserJWT

router = APIRouter()

@router.get("/meetings", response_model=List[MeetingCollection])
async def list_meetings(
    skip: int = 0, 
    limit: int = 50,
    current_user: UserJWT = Depends(get_current_user)
):
    """
    List all generated meetings (MoMs).
    """
    return await MeetingsController.get_all_meetings(current_user, skip, limit)

@router.get("/meetings/{meeting_id}", response_model=MeetingCollection)
async def get_meeting(
    meeting_id: PydanticObjectId,
    current_user: UserJWT = Depends(get_current_user)
):
    """
    Get a specific meeting by ID.
    """
    meeting = await MeetingsController.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

from fastapi.responses import HTMLResponse

@router.get("/meetings/{meeting_id}/print", response_class=HTMLResponse)
async def get_meeting_print(
    meeting_id: PydanticObjectId,
    current_user: UserJWT = Depends(get_current_user)
):
    """
    Get printable HTML for a meeting.
    """
    html_content = await MeetingsController.generate_html(meeting_id)
    if not html_content:
        raise HTTPException(status_code=404, detail="Meeting not found or template error")
    return html_content
