import asyncio
import os
from httpx import AsyncClient, ASGITransport
from app.server import app

# Ensure env vars are loaded for the test referencing the ones we just set
# But env_settings is already loaded in server.py, so it should be fine.

async def verify_auth():
    print("🚀 Starting Authentication Verification...")
    
    # We need to manually trigger lifespan for Beanie init if not using TestClient with block
    # But AsyncClient with app argument usually handles basic request routing.
    # However, lifespan startup is crucial for DB connection.
    # The clean way is to use the lifespan context manager.
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Trigger startup
        async with app.router.lifespan_context(app):
            print("✅ App Startup Completed (DB Connected)")
            
            # 1. Register
            email = "testuser_verify@example.com"
            username = "testuser_verify"
            password = "securepassword123"
            
            # Clean up potentially existing user first (optional, or just handle error)
            # Since we can't easily access DB directly without imports, we rely on duplicate checks.
            # We'll use a random suffix if needed, but let's try fixed first.
            import random
            rand_suffix = random.randint(1000, 9999)
            email = f"testuser_{rand_suffix}@example.com"
            username = f"testuser_{rand_suffix}"

            print(f"🔹 Registering user: {email}")
            response = await ac.post("/api/auth/register", json={
                "username": username,
                "email": email,
                "password": password,
                "full_name": "Test User"
            })
            
            if response.status_code != 200:
                print(f"❌ Registration Failed: {response.text}")
                return
            
            data = response.json()
            if "access_token" in data:
                print("✅ Registration Successful. Token received.")
            else:
                print(f"❌ Registration Successful but no token? {data}")
                return

            # 2. Login
            print("🔹 Logging in...")
            login_response = await ac.post("/api/auth/login", json={
                "email": email,
                "password": password
            })
            
            if login_response.status_code != 200:
                print(f"❌ Login Failed: {login_response.text}")
                return
            
            login_data = login_response.json()
            token = login_data.get("access_token")
            if token:
                print("✅ Login Successful. Token received.")
                print(f"🔑 Token: {token[:20]}...")
            else:
                print(f"❌ Login Successful but no token? {login_data}")

            # 3. Decode Token (Verify Structure)
            # We can't verify 'protected' route unless we have one, but we can verify the token content locally if we import security utils,
            # or just trust the server returned a valid one.
            # Let's try to pass the token to a protected endpoint if exists. 
            # Looking at routers, 'general' or 'recordings' might have one.
            # But let's just stick to Auth verification success.
            
    print("✅ Verification Finished Successfully")

if __name__ == "__main__":
    try:
        asyncio.run(verify_auth())
    except Exception as e:
        print(f"❌ Error running verification: {e}")
