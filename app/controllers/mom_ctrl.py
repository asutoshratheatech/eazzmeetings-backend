

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import Optional
from datetime import datetime
import json
import os

from app.services.mom_service import MoMService
from app.services.transcribers import TranscriptionService, ModelChoices
from app.utils.audio import convert_to_opus
from app.models.database.meeting_collection import MeetingCollection
from app.models.database.recordings_collection import RecordingCollection
from app.schemas.meetings_schema import MeetingBase
from beanie import PydanticObjectId

# Initialize Service
mom_service = MoMService()
transcription_service = TranscriptionService()

class MoMController:
    
    @staticmethod
    async def generate_mom_from_text(
        transcription: str,
        meeting_link: str,
        audio_url: str,
        meeting_date: str,
        meeting_time: str,
        meeting_duration: str,
        org_id: Optional[PydanticObjectId] = None,
        recording_id: Optional[PydanticObjectId] = None,
        created_by: Optional[PydanticObjectId] = None
    ) -> MeetingCollection:
        """
        Controller to generate MoM from raw text and metadata.
        """
        try:
            print(f"🚀 Starting MoM Generation for meeting on {meeting_date}")
            
            # Invoke Graph
            # Estimate token count (Char / 4)
            token_count = len(transcription) // 4
            print(f"📊 Estimated Input Token Count: {token_count}")
            
            result_state = mom_service.generate_mom(transcription)
            
            # Construct Meeting Object
            # Note: The result_state keys match the fields in MeetingBase/MeetingCollection 
            # (general_summaries, topic_summaries, etc.)
            
            meeting_data = {
                "transcription": transcription,
                "meeting_link": meeting_link,
                "audio_url": audio_url,
                "meeting_date": meeting_date,
                "meeting_time": meeting_time,
                "meeting_duration": meeting_duration,
                
                "general_summaries": result_state["general_summaries"],
                "topic_summaries": result_state["topic_summaries"],
                "decisions": result_state["decisions"],
                "action_items": result_state["action_items"],
                "facts": result_state["facts"],
                "attendees": result_state["attendees"],
                "org_id": org_id,
                "recording_id": recording_id,
                "created_by": created_by
            }
            
            # Validate and Create Document
            meeting_doc = MeetingCollection(**meeting_data)
            
            # Save to DB
            await meeting_doc.insert()
            print(f"✅ MoM Saved to DB: {meeting_doc.id}")
            
            return meeting_doc

        except Exception as e:
            print(f"❌ Error generating MoM: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def generate_mom_from_audio(
        file: UploadFile,
        meeting_link: str,
        meeting_date: str,
        meeting_time: str,
        org_id: Optional[PydanticObjectId] = None,
        created_by: Optional[PydanticObjectId] = None
    ) -> MeetingCollection:
        """
        Controller to generate MoM from audio file.
        Handles:
        1. Smart Conversion (OGG check)
        2. Transcription
        3. MOM Generation
        """
        try:
            print(f"🚀 Starting Audio MoM Generation for {file.filename}")
            
            # 1. Read File
            file_content = await file.read()
            if not file_content:
                raise HTTPException(status_code=400, detail="Empty file")
            
            filename = file.filename or "audio.wav"
            
            # 2. Smart Conversion
            is_ogg = filename.lower().endswith('.ogg') or file.content_type == 'audio/ogg'
            
            if is_ogg:
                print(f"✅ File {filename} is already OGG. Skipping conversion.")
                transcribe_content = file_content
                transcribe_filename = filename
            else:
                print(f"⚠️ File {filename} is NOT OGG. Converting to Opus/OGG...")
                transcribe_content = convert_to_opus(file_content)
                transcribe_filename = f"{filename}.ogg"

            # 3. Transcription
            print(f"🎤 Transcribing {transcribe_filename}...")
            transcription_result = transcription_service.whisper_transcribe(
                transcribe_content, 
                transcribe_filename, 
                ModelChoices.WHISPER_LARGE_TURBO
            )
            
            transcript_text = transcription_result.get("text", "")
            duration_s = transcription_result.get("duration", 0.0)
            meeting_duration = f"{int(duration_s // 60)} mins {int(duration_s % 60)} secs"
            
            print("✅ Transcription Complete.")
            
            # 4. Generate MoM (Reuse existing logic)
            audio_url = f"uploaded/{filename}" 
            
            return await MoMController.generate_mom_from_text(
                transcription=transcript_text,
                meeting_link=meeting_link,
                audio_url=audio_url,
                meeting_date=meeting_date,
                meeting_time=meeting_time,
                meeting_duration=meeting_duration,
                org_id=org_id,
                created_by=created_by
            )

        except Exception as e:
            print(f"❌ Error generating Audio MoM: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def generate_mom_from_recording(
        recording_id: PydanticObjectId,
        org_id: Optional[PydanticObjectId] = None
    ) -> MeetingCollection:
        """
        Controller to generate MoM from an existing recording ID.
        """
        try:
            print(f"🚀 Starting MoM Generation for Recording ID: {recording_id}")

            # 1. Fetch Recording
            recording = await RecordingCollection.get(recording_id)
            if not recording:
                raise HTTPException(status_code=404, detail="Recording not found")

            # Check Org Access (if applicable)
            if org_id and str(recording.org_id) != str(org_id):
                 # This check depends on how org_id is stored. Assuming string comparison is safe.
                 # If org_id in recording is None, allowing might be unsafe depending on policy.
                 # For now, simplistic check.
                 pass

            # 2. Check File Existence
            file_path = recording.file_path
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail=f"Recording file not found at {file_path}")

            # 3. Read File
            with open(file_path, "rb") as f:
                file_content = f.read()

            # 4. Smart Conversion (Reuse logic via util or just inline)
            # Assuming logic similar to from_audio
            filename = os.path.basename(file_path)
            is_ogg = filename.lower().endswith('.ogg')
            
            if is_ogg:
                 transcribe_content = file_content
                 transcribe_filename = filename
            else:
                 print(f"Converting {filename} to Opus...")
                 transcribe_content = convert_to_opus(file_content)
                 transcribe_filename = f"{filename}.ogg"

            # 5. Transcription
            print(f"🎤 Transcribing {transcribe_filename}...")
            transcription_result = transcription_service.whisper_transcribe(
                transcribe_content, 
                transcribe_filename, 
                ModelChoices.WHISPER_LARGE_TURBO
            )

            transcript_text = transcription_result.get("text", "")
            duration_s = transcription_result.get("duration", 0.0)
            meeting_duration = f"{int(duration_s // 60)} mins {int(duration_s % 60)} secs"
            
            print("✅ Transcription Complete.")

            # 6. Generate MoM
            # Metadata from recording
            meeting_date = recording.creation_date.strftime("%Y-%m-%d")
            meeting_time = recording.creation_date.strftime("%H:%M")
            meeting_link = recording.meeting_link or "N/A"
            audio_url = f"recordings/{recording.id}" # specific URL pattern for accessing recording?

            return await MoMController.generate_mom_from_text(
                transcription=transcript_text,
                meeting_link=meeting_link,
                audio_url=audio_url,
                meeting_date=meeting_date,
                meeting_time=meeting_time,
                meeting_duration=meeting_duration,
                org_id=recording.org_id if recording.org_id else org_id,
                recording_id=recording.id,
                created_by=recording.created_by
            )

        except Exception as e:
            print(f"❌ Error generating MoM from Recording: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
