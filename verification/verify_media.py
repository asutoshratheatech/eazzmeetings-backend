
import httpx
import asyncio
import os
import sys
import json

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

BASE_URL = "http://localhost:8000/api"
TEST_RESULTS_DIR = "test_results"
SAMPLE_FILE = os.path.join("recordings", "samples", "mcl2audio_optimized.flac")

if not os.path.exists(TEST_RESULTS_DIR):
    os.makedirs(TEST_RESULTS_DIR)

async def login(client):
    """Logs in and returns the access token."""
    print("🔹 Logging in...")
    import random
    rand_suffix = random.randint(10000, 99999)
    email = f"media_{rand_suffix}@test.com"
    username = f"media_user_{rand_suffix}"
    password = "password123"

    # Register
    try:
        await client.post(f"{BASE_URL}/auth/register", json={
            "username": username,
            "email": email,
            "password": password,
            "full_name": "Media Tester",
            "phone": (91, 1234567890)
        })
    except Exception as e:
        print(f"⚠️ Registration warning: {e}")

    response = await client.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login success")
        return token
    else:
        print(f"❌ Login failed: {response.text}")
        return None

async def verify_convert_flac(client, token):
    print("\n🔹 Testing Convert to FLAC...")
    headers = {"Authorization": f"Bearer {token}"}
    
    if not os.path.exists(SAMPLE_FILE):
        print(f"❌ Sample file not found: {SAMPLE_FILE}")
        return

    with open(SAMPLE_FILE, "rb") as f:
        files = {"file": (os.path.basename(SAMPLE_FILE), f, "audio/flac")}
        response = await client.post(f"{BASE_URL}/convert/flac", files=files, headers=headers)
        
    if response.status_code == 200:
        output_path = os.path.join(TEST_RESULTS_DIR, "output.flac")
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"✅ Convert FLAC success. Saved to {output_path}")
    else:
        print(f"❌ Convert FLAC failed: {response.status_code} - {response.text}")

async def verify_convert_opus(client, token):
    print("\n🔹 Testing Convert to Opus...")
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(SAMPLE_FILE, "rb") as f:
        files = {"file": (os.path.basename(SAMPLE_FILE), f, "audio/flac")}
        response = await client.post(f"{BASE_URL}/convert/opus", files=files, headers=headers)
        
    if response.status_code == 200:
        output_path = os.path.join(TEST_RESULTS_DIR, "output.ogg")
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"✅ Convert Opus success. Saved to {output_path}")
    else:
        print(f"❌ Convert Opus failed: {response.status_code} - {response.text}")

async def verify_transcribe(client, token):
    print("\n🔹 Testing Transcribe (using output.ogg)...")
    headers = {"Authorization": f"Bearer {token}"}
    
    ogg_file = os.path.join(TEST_RESULTS_DIR, "output.ogg")
    if not os.path.exists(ogg_file):
        print(f"❌ OGG file not found: {ogg_file}")
        return

    with open(ogg_file, "rb") as f:
        files = {"file": ("output.ogg", f, "audio/ogg")}
        # Use turbo model for speed if available, or default
        response = await client.post(f"{BASE_URL}/transcribe", files=files, headers=headers)
        
    if response.status_code == 200:
        data = response.json()
        output_path = os.path.join(TEST_RESULTS_DIR, "transcription.json")
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Transcribe success. Saved to {output_path}")
        print(f"   Text preview: {data.get('text', '')[:100]}...")
    else:
        print(f"❌ Transcribe failed: {response.status_code} - {response.text}")

async def main():
    async with httpx.AsyncClient(timeout=600.0) as client: # Long timeout for transcription
        # Check if server is up
        try:
            await client.get(f"{BASE_URL}/")
            print("✅ Server is reachable")
        except Exception:
            print("❌ Server seems down. Please start it with: uv run main.py")
            return

        token = await login(client)
        if token:
            await verify_convert_flac(client, token)
            await verify_convert_opus(client, token)
            await verify_transcribe(client, token)

if __name__ == "__main__":
    asyncio.run(main())
