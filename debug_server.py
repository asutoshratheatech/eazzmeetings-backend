
import sys
import os

print("Attempting to import app.server...")
try:
    from app.server import app
    print("✅ Successfully imported app.server")
except ImportError as e:
    print(f"❌ ImportError: {e}")
except Exception as e:
    print(f"❌ Exception during import: {e}")
