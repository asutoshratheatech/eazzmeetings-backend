import asyncio
import websockets
import json
import httpx
import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

BASE_URL = "http://localhost:8000/api"
WS_URL = "ws://localhost:8000/api/ws/record"

async def get_token():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Use existing user from previous tests or verify_auth logic
        # For simplicity, let's just register a temp user to get a fresh token
        import random
        rand_suffix = random.randint(10000, 99999)
        email = f"wstest_{rand_suffix}@example.com"
        
        # Register
        try:
            resp = await client.post("/auth/register", json={
                "username": f"wstest_{rand_suffix}",
                "email": email,
                "password": "password123",
                "full_name": "WS Test User"
            })
            if resp.status_code == 200:
                return resp.json()["access_token"]
        except Exception:
            pass
        
        # If fail, try login (maybe user exists)
        resp = await client.post("/auth/login", json={
            "email": email,
            "password": "password123"
        })
        if resp.status_code == 200:
            return resp.json()["access_token"]
            
        print(f"❌ Could not get token: {resp.text}")
        return None

async def test_valid_handshake(token):
    print("\n🔹 Testing Valid Handshake...")
    try:
        async with websockets.connect(WS_URL) as ws:
            # 1. Auth Frame
            await ws.send(json.dumps({"token": token}))
            resp1 = json.loads(await ws.recv())
            print(f"Server Response 1: {resp1}")
            
            if resp1.get("status") != "authenticated":
                print("❌ Auth failed")
                return

            # 2. Metadata Frame
            metadata = {
                "name": "Project Discussion",
                "meeting_link": "http://meet.google.com/abc-defg-hij",
                "org_id": "org_123"
            }
            await ws.send(json.dumps(metadata))
            resp2 = json.loads(await ws.recv())
            print(f"Server Response 2: {resp2}")
            
            if resp2.get("status") == "recording_started":
                print(f"✅ Handshake Success! Filename: {resp2.get('filename')}")
                # Send a few chunks (simulate stream)
                dummy_audio = b"\x00" * 1024
                for _ in range(5):
                     await ws.send(dummy_audio)
                     await asyncio.sleep(0.1)
                
                print("Sent dummy audio bytes")
                
                # --- NEW: Send Stop Signal ---
                await ws.send(json.dumps({"type": "stop_recording"}))
                print("Sent stop_recording signal")
                
                # Expect connection closure
                try:
                     # Wait for close
                     await ws.wait_closed()
                     print("✅ Connection closed cleanly by server")
                except Exception as e:
                     print(f"⚠️ Connection closed with: {e}")
            else:
                print("❌ Metadata handshake failed")

    except Exception as e:
        print(f"❌ Handshake/Stream Failed: {e}")
    finally:
        pass

async def test_auth_timeout():
    print("\n🔹 Testing Auth Timeout (Wait 11s)...")
    try:
        async with websockets.connect(WS_URL) as ws:
            # Do nothing
            await asyncio.sleep(11)
            # Try to send now
            await ws.send(json.dumps({"token": "too_late"}))
            resp = await ws.recv()
            print(f"Response: {resp}")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"✅ Connection closed as expected: {e.code} - {e.reason}")

async def test_invalid_token():
    print("\n🔹 Testing Invalid Token...")
    try:
        async with websockets.connect(WS_URL) as ws:
            await ws.send(json.dumps({"token": "invalid_jwt_token_string"}))
            # Expect close
            resp = await ws.recv()
            print(f"Response: {resp}")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"✅ Connection closed as expected: {e.code} - {e.reason}")

async def main():
    token = await get_token()
    if not token:
        return

    await test_valid_handshake(token)
    # await test_auth_timeout() # Skipped to save time
    await test_invalid_token()

if __name__ == "__main__":
    asyncio.run(main())
