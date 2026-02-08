from app.security import verify_password, get_password_hash, create_access_token, decode_token
from app.env_settings import env
from app.schemas.common_schema import UserJWT
import datetime
import asyncio

def test_security():
    print("🔐 Testing Security Utilities...")
    
    # 1. Password Hashing
    password = "supersecretpassword"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) == True
    assert verify_password("wrongpassword", hashed) == False
    print("✅ Password Hashing/Verification: OK")
    
    # 2. JWT Token
    data = {"sub": "user123", "org_id": "org456"}
    token = create_access_token(data)
    assert isinstance(token, str)
    
    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user123"
    assert decoded["org_id"] == "org456"
    assert "exp" in decoded
    print("✅ JWT Token Creation/Decoding: OK")
    
    print("✅ Security Utilities Verification Passed")

if __name__ == "__main__":
    test_security()
