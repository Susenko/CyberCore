import os
import json
import websocket
from dotenv import load_dotenv
import base64
import pyaudio

# Load environment variables from .env file
load_dotenv()

# Get API Key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ensure API Key is set
if not OPENAI_API_KEY:
    raise ValueError("❌ ERROR: OPENAI_API_KEY is not set. Check your .env file or environment variables.")

# OpenAI's expected audio sample rate (reduce speed issue)
SAMPLE_RATE = 24000  # OpenAI audio is usually 16 kHz
CHANNELS = 1
FORMAT = pyaudio.paInt16

# Initialize PyAudio for playback
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=SAMPLE_RATE,  # Ensure correct playback rate
                output=True)


# OpenAI Realtime API WebSocket URL
url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
headers = [
    f"Authorization: Bearer {OPENAI_API_KEY}",
    "OpenAI-Beta: realtime=v1"
]

def on_open(ws):
    print("✅ Connected to OpenAI")

    # Sending a simple instruction
    event = {
        "type": "response.create",
        "response": {
            "modalities": ["text", "audio"],
            "instructions": "Please assist the user."
        }
    }
    ws.send(json.dumps(event))
    print("📤 Sent request to OpenAI")

def on_message(ws, message):
    data = json.loads(message)
    print("📩 Received response:", json.dumps(data, indent=2))

    # Check if the response contains audio data
    if data.get("type") == "response.audio.delta" and "delta" in data:
        audio_data = data["delta"]  # Base64-encoded audio

        # Decode base64 audio data to raw PCM16 bytes
        audio_bytes = base64.b64decode(audio_data)

        # Play the audio bytes in real-time
        stream.write(audio_bytes)

        print("🎵 Playing received audio...")


ws = websocket.WebSocketApp(
    url,
    header=headers,
    on_open=on_open,
    on_message=on_message,
)

ws.run_forever()
