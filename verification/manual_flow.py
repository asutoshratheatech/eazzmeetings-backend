
import asyncio
import os
import requests
import json
from dotenv import load_dotenv

# Adjust path to app if needed
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.transcribers import TranscriptionService, ModelChoices

# Load env
load_dotenv(".env.development")

BASE_URL = "http://localhost:8008"
EMAIL = os.getenv("stable_test_email")
PASSWORD = os.getenv("stable_test_password")
AUDIO_FILE = r'd:\Work\EATech\project-eazzmeetings\eazzmeetings\test_results\output.ogg'

def login():
    print("🔹 Logging in...")
    login_url = f"{BASE_URL}/api/auth/login"
    response = requests.post(login_url, json={"email": EMAIL, "password": PASSWORD}, timeout=10)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return None
    print("✅ Login success")
    return response.json().get("access_token")

def transcribe_and_call_mom():
    if not os.path.exists(AUDIO_FILE):
        print(f"❌ Audio file not found: {AUDIO_FILE}")
        return

    # print(f"🎤 Transcribing {AUDIO_FILE} locally...")
    # service = TranscriptionService()
    
    # with open(AUDIO_FILE, "rb") as f:
    #     file_content = f.read()
    
    # # Use Turbo model
    # try:
    #     result = service.whisper_transcribe(file_content, "output.ogg", ModelChoices.WHISPER_LARGE_TURBO)
    #     transcript_text = result.get("text", "")
    # except Exception as e:
    #     print(f"⚠️ Transcription failed (likely rate limit): {e}")
    #     print("🔹 Using mock transcript for MoM testing.")
    #     transcript_text = "This is a meeting about project updates. " * 500 # Approx 3500 words -> ~4500 tokens
    
    print("🔹 Using mock transcript for MoM testing (Bypassing Whisper Rate Limit).")
    transcript_text = "The team discussed the Q3 goals. John mentioned that we are on track. Sarah raised a concern about the budget. " * 300
    
    token_count = len(transcript_text) // 4
    print(f"\n📝 Transcription Length: {len(transcript_text)} chars")
    print(f"\n📝 Transcription Length: {len(transcript_text)} chars")
    print(f"📊 Estimated Token Count: {token_count}")
    
    if token_count > 30000: # Arbitrary high limit check
        print("⚠️ Warning: Token count is very high!")

    # Now call the MoM API
    token = login()
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}
    
    data = {
        "transcription": transcript_text,
        "meeting_link": "http://test.com",
        "audio_url": "http://test.com/output.ogg",
        "meeting_date": "2024-10-26",
        "meeting_time": "11:00 AM",
        "meeting_duration": "15 mins"
    }

    print("\n🔹 Calling /mom/generate API...")
    url = f"{BASE_URL}/api/mom/generate"
    response = requests.post(url, json=data, headers=headers, timeout=300)

    if response.status_code == 200:
        print("✅ MoM Generation Success!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ MoM Failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    transcribe_and_call_mom()
