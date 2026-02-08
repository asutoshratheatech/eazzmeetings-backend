import httpx
import asyncio
import os
import wave
import struct
import math
import random
import sys

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


BASE_URL = "http://localhost:8000/api"

def generate_sine_wave(filename, duration=1.0, freq=440.0, rate=44100):
    """Generates a mono WAV file with a sine wave."""
    nframes = int(duration * rate)
    with wave.open(filename, 'wb') as obj:
        obj.setnchannels(1) # mono
        obj.setsampwidth(2) # 2 bytes (16 bit)
        obj.setframerate(rate)
        data = []
        for i in range(nframes):
            value = int(math.sin(2 * math.pi * freq * i / rate) * 32767.0)
            data.append(struct.pack('<h', value))
        obj.writeframes(b''.join(data))
    print(f"🎵 Generated test audio: {filename}")

async def login(client):
    """Logs in and returns the access token."""
    print("🔹 Logging in...")
    import random
    rand_suffix = random.randint(10000, 99999)
    email = f"audio_{rand_suffix}@test.com"
    username = f"audio_user_{rand_suffix}"
    password = "password123"

    # Register
    try:
        reg_resp = await client.post(f"{BASE_URL}/auth/register", json={
            "username": username,
            "email": email,
            "password": password,
            "full_name": "Audio Tester",
            "phone": (91, 1234567890)
        })
        print(f"🔹 Registration Reponse: {reg_resp.status_code} - {reg_resp.text}")
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

async def verify_upload(client, token):
    print("\n🔹 Testing Manual Upload...")
    if not token:
        print("❌ Skipping upload test (no token)")
        return

    filename = "test_upload.wav"
    generate_sine_wave(filename, duration=2.0)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(filename, "rb") as f:
        files = {"file": (filename, f, "audio/wav")}
        response = await client.post(f"{BASE_URL}/recordings/upload", files=files, headers=headers)
        
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Upload success: {data}")
        # Verify file exists
        outfile = os.path.join("recordings", data["filename"])
        if os.path.exists(outfile):
            print(f"✅ Output file exists: {outfile}")
            # Check for OGG header
            with open(outfile, "rb") as f:
                header = f.read(4)
                if header == b'OggS':
                    print("✅ Output file has OGG header")
                else:
                    print(f"❌ Invalid header: {header}")
            
            # Verify DB ID returned
            if "recording_id" in data:
                 print(f"✅ DB Record Created: {data['recording_id']}")
            else:
                 print("❌ No recording_id in response")

        else:
            print("❌ Output file not found")
    else:
        print(f"❌ Upload failed: {response.status_code} - {response.text}")
    
    if os.path.exists(filename):
        os.remove(filename)


async def verify_streaming(client):
    print("\n🔹 Testing Streaming...")
    # Generate 3 chunks
    session_id = f"test_session_{random.randint(1000,9999)}"
    
    chunks = []
    for i in range(3):
        fname = f"chunk_{i}.wav"
        generate_sine_wave(fname, duration=1.0, freq=440 + (i*100))
        chunks.append(fname)
        
    for i, fname in enumerate(chunks):
        with open(fname, "rb") as f:
            files = {"file": (fname, f, "audio/wav")}
            data = {"session_id": session_id, "chunk_index": i}
            response = await client.post(f"{BASE_URL}/recordings/stream", files=files, data=data)
            
        if response.status_code == 200:
            print(f"✅ Chunk {i} success: {response.json()}")
        else:
            print(f"❌ Chunk {i} failed: {response.status_code} - {response.text}")
        
        os.remove(fname)
        
    # Check appended file
    outfile = os.path.join("recordings", f"{session_id}.ogg")
    if os.path.exists(outfile):
        size = os.path.getsize(outfile)
        print(f"✅ Stream session file exists: {outfile} (Size: {size} bytes)")
        if size > 0:
            print("✅ File has content")
    else:
        print("❌ Stream session file not found")

async def main():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Check if server is up
        try:
            await client.get(f"{BASE_URL}/")
            print("✅ Server is reachable")
        except Exception:
            print("❌ Server seems down or not reachable at localhost:8000")
            print("   Please start the server with: uv run main.py")
            return

        token = await login(client)
        await verify_upload(client, token)
        await verify_streaming(client)

if __name__ == "__main__":
    asyncio.run(main())
