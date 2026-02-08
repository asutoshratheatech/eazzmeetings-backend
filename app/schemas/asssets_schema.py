from pydantic import BaseModel, HttpUrl



class Meeting(BaseModel):
    meet_link: HttpUrl
    meet_transcription_raw: str
    meet_recording_audios: list[HttpUrl]
    meet_notes_images: list[HttpUrl]
    meet_summary: str
    meet_action_items: list[str]    
    
    # user: Link

