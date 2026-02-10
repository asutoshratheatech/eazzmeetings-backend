
import os
import requests
import json
from dotenv import load_dotenv

# Load env
load_dotenv(".env.development")

# BASE_URL = os.getenv("BACKEND", "http://localhost:8007")
BASE_URL = "http://localhost:8007"
EMAIL = os.getenv("stable_test_email")
PASSWORD = os.getenv("stable_test_password")

def test_mom_generation():
    # Login
    print("🔹 Logging in...")
    login_url = f"{BASE_URL}/api/auth/login"
    response = requests.post(login_url, json={"email": EMAIL, "password": PASSWORD}, timeout=10)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return
    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login success")

    # Sample Transcript
    transcript = """
    Meeting Date: 2024-10-25
    Attendees: Alice (Product Manager), Bob (Engineering Lead), Charlie (Designer)
    
    Alice: Let's start the meeting. The main goal today is to decide on the UI framework for the new dashboard.
    Bob: I suggest we use React because the team is already familiar with it.
    Charlie: valid point, but Vue might be lighter. However, React has better library support.
    Alice: Okay, agreed. Let's go with React.
    Bob: I will set up the repository by tomorrow.
    Charlie: I'll have the wireframes ready by Wednesday.
    Alice: Great. Also, we need to hire a new backend dev. The budget is approved.
    Alice: Bob, can you also look into the CI/CD pipeline issues?
    Bob: Sure, I'll add that to my list.
    """

    data = {
        "transcription": transcript,
        "meeting_link": "http://meet.google.com/abc-defg-hij",
        "audio_url": "http://s3.aws.com/audio/123.mp3",
        "meeting_date": "2024-10-25",
        "meeting_time": "10:00 AM",
        "meeting_duration": "30 mins"
    }

    print("🔹 Generating MoM (this may take a few seconds)...")
    url = f"{BASE_URL}/api/mom/generate"
    print(f"🔹 Requesting URL: {url}")
    response = requests.post(url, json=data, headers=headers, timeout=300)

    if response.status_code == 200:
        print("✅ MoM Generation Success!")
        mom = response.json()
        print(json.dumps(mom, indent=2))
        
        # Validation
        try:
            assert mom["general_summaries"], "General Summary missing"
            # Decisions might be a list or a nested object depending on schema
            # Decisions schema: class Decisions(BaseModel): decisions: List[Decision]
            assert len(mom["decisions"]["decisions"]) > 0, "Decisions missing"
            assert len(mom["action_items"]["action_items"]) > 0, "Action Items missing"
            print("✅ Verification Passed: Structure Valid")
        except AssertionError as e:
            print(f"❌ Verification Failed: {e}")
        
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")


def test_audio_mom_generation():
    print("\n🔹 Testing Audio MoM Generation...")
    # Login
    login_url = f"{BASE_URL}/api/auth/login"
    response = requests.post(login_url, json={"email": EMAIL, "password": PASSWORD}, timeout=10)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return
    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # Use existing sample OGG file
    audio_filename = r'd:\Work\EATech\project-eazzmeetings\eazzmeetings\test_results\output.ogg'
    if not os.path.exists(audio_filename):
        print(f"❌ Audio file not found: {audio_filename}")
        return

    # files = {'file': (audio_filename, open(audio_filename, 'rb'), 'audio/wav')}
    # For OGG, use correct mime type
    files = {'file': ('output.ogg', open(audio_filename, 'rb'), 'audio/ogg')}

    data = {
        "meeting_link": "http://test.com",
        "audio_url": "http://test.com/audio.wav",
        "meeting_date": "2024-10-26",
        "meeting_time": "11:00 AM",
        "meeting_duration": "15 mins"
    }
    
    url = f"{BASE_URL}/api/mom/generate-from-audio"
    print(f"🔹 Requesting URL: {url}")
    # Note: requests.post with files ignores 'json' param, use 'data' for fields
    response = requests.post(url, data=data, files=files, headers=headers, timeout=300)
    
    if response.status_code == 200:
        print("✅ Audio MoM Generation Success!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Audio MoM Failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    # test_mom_generation()
    # Uncomment to test audio (requires a valid audio file)
    test_audio_mom_generation()

