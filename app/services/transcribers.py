

import json
from enum import Enum
# from mistralai import Mistral
from groq import Groq
from app.env_settings import env

class ModelChoices(str,Enum):
    WHISPER_LARGE_TURBO = "whisper-large-v3-turbo"
    WHISPER_LARGE = "whisper-large-v3"


class TranscriptionService:
    def __init__(self):
        # self.mistral= Mistral(api_key=env.MISTRAL_API_KEY) if env.MISTRAL_API_KEY else None
        self.groq= Groq(api_key=env.GROQ_API_KEY)
    
    def whisper_transcribe(self, file_content: bytes, filename: str, model: ModelChoices = ModelChoices.WHISPER_LARGE):
        print(model)
        # Handle model being an Enum or a string
        model_id = model.value if hasattr(model, 'value') else model
        print(f"Using model ID: {model_id}")
        transcription = self.groq.audio.transcriptions.create(
            file=(filename, file_content),
            response_format='verbose_json',
            model=model_id,
            timestamp_granularities=["word", "segment"]
        )
        return transcription.to_dict()



if __name__ == "__main__":
    transcription_service = TranscriptionService()
    with open(r'D:\Work\EATech\project-eazzmeetings\eazzmeetings\test_results\output.ogg', 'rb') as f:
        transcription=transcription_service.whisper_transcribe(f.read(), 'output.ogg',model=ModelChoices.WHISPER_LARGE_TURBO) 
    with open(r'D:\Work\EATech\project-eazzmeetings\eazzmeetings\test_results\output.json', 'w') as f:
        json.dump(transcription, f)
    