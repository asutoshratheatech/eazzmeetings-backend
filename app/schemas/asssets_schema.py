from pydantic import BaseModel, HttpUrl



class MeetingAssets(BaseModel):
    """
        The root model containing all extraction categories.
    """
    meet_link: HttpUrl
    meet_transcription_raw: str
    meet_recording_audios: list[HttpUrl]
    meet_notes_images: list[HttpUrl]
    meet_summary: str
    meet_action_items: list[str]

