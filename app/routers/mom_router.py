
from fastapi import APIRouter, Body, HTTPException, Depends, UploadFile, File, Form
from pydantic import HttpUrl

from app.controllers.mom_ctrl import MoMController
from app.models.database.meeting_collection import MeetingCollection
from app.schemas.mom_schema import GenerateMoMRequest
from app.security import get_current_user
from app.schemas.common_schema import UserJWT
from beanie import PydanticObjectId

router = APIRouter()


@router.post("/mom/generate", response_model=MeetingCollection)
async def generate_mom_endpoint(
    request: GenerateMoMRequest,
    current_user: UserJWT = Depends(get_current_user)
):
    """
    Generate Minutes of Meeting (MoM) from a transcript.
    """
    org_id = current_user.get("org_id")
    # if org_id is None, it might be in the user collection, but for now we assume it's in token or None
    # If strictly required, we should fetch user. But let's pass what we have.
    # The UserJWT TypedDict defines org_id as Optional[str]. We might need to convert to PydanticObjectId if it's a valid ID.
    
    oid = PydanticObjectId(org_id) if org_id else None

    user_id = current_user.get("sub")
    uid = PydanticObjectId(user_id) if user_id else None

    return await MoMController.generate_mom_from_text(
        transcription=request.transcription,
        meeting_link=str(request.meeting_link),
        audio_url=str(request.audio_url),
        meeting_date=request.meeting_date,
        meeting_time=request.meeting_time,
        meeting_duration=request.meeting_duration,
        org_id=oid,
        created_by=uid
    )

@router.post("/mom/generate-from-audio", response_model=MeetingCollection)
async def generate_mom_from_audio_endpoint(
    file: UploadFile = File(...),
    meeting_link: str = Form(...),
    meeting_date: str = Form(...),
    meeting_time: str = Form(...),
    current_user: UserJWT = Depends(get_current_user)
):
    """
    Generate MoM from an audio file.
    Accepts audio file, converts if necessary, transcribes, and generates MoM.
    """
    org_id = current_user.get("org_id")
    oid = PydanticObjectId(org_id) if org_id else None
    
    user_id = current_user.get("sub")
    uid = PydanticObjectId(user_id) if user_id else None

    return await MoMController.generate_mom_from_audio(
        file=file,
        meeting_link=meeting_link,
        meeting_date=meeting_date,
        meeting_time=meeting_time,
        org_id=oid,
        created_by=uid
    )

@router.post("/mom/generate-from-recording/{recording_id}", response_model=MeetingCollection)
async def generate_mom_from_recording_endpoint(
    recording_id: PydanticObjectId,
    current_user: UserJWT = Depends(get_current_user)
):
    """
    Generate MoM from an existing recording.
    """
    org_id = current_user.get("org_id")
    oid = PydanticObjectId(org_id) if org_id else None

    return await MoMController.generate_mom_from_recording(
        recording_id=recording_id,
        org_id=oid
    )
