import os
import sys
# Add parent directory to path to allow importing 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import math
import struct
import wave
from app.services.transcriber import TranscriberService, TranscriptionOptions, TranscriptionProvider, MistralModel

# Generate a small dummy audio file (silent or tone)
def generate_sine_wave(filename, duration=1.0):
    with wave.open(filename, 'wb') as obj:
        obj.setnchannels(1)
        obj.setsampwidth(2)
        obj.setframerate(16000)
        nframes = int(duration * 16000)
        data = []
        for i in range(nframes):
            value = int(math.sin(2 * math.pi * 440 * i / 16000) * 32767.0)
            data.append(struct.pack('<h', value))
        obj.writeframes(b''.join(data))

def main():
    service = TranscriberService()
    filename = "test_transcribe.wav"
    generate_sine_wave(filename, duration=2.0)
    print(f"🎵 Created dummy audio: {filename}")

    # 1. Test Groq
    print("\n🔹 Testing Groq (Whisper)...")
    try:
        opts = TranscriptionOptions(
            provider=TranscriptionProvider.GROQ
        )
        res = service.transcribe(filename, opts)
        print(f"✅ Groq Result: '{res['text']}'")
    except Exception as e:
        print(f"❌ Groq Failed: {e}")

    # 2. Test Mistral
    print("\n🔹 Testing Mistral (Voxtral)...")
    try:
        opts = TranscriptionOptions(
            provider=TranscriptionProvider.MISTRAL,
            model=MistralModel.VOXTRAL_MINI_LATEST
        )
        # Note: Depending on API key availability this might fail
        res = service.transcribe(filename, opts)
        print(f"✅ Mistral Text: '{res['text']}'")
    except Exception as e:
        print(f"❌ Mistral Failed: {e}")

    if os.path.exists(filename):
        os.remove(filename)

if __name__ == "__main__":
    main()
