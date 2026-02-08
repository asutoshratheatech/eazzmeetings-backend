from mistralai import Mistral
import inspect

try:
    print("Inspecting Mistral SDK...")
    client = Mistral(api_key="DUMMY")
    
    if hasattr(client, 'audio'):
        print("✅ client.audio exists")
        if hasattr(client.audio, 'transcriptions'):
             print("✅ client.audio.transcriptions exists")
             method = client.audio.transcriptions.complete
             print(f"Method: {method}")
             sig = inspect.signature(method)
             print(f"Signature: {sig}")
        else:
             print("❌ client.audio.transcriptions MISSING")
    else:
        print("❌ client.audio MISSING")

except Exception as e:
    print(f"Error inspecting: {e}")
