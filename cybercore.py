import os
import json
import websocket
import base64
import pyaudio
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ ERROR: OPENAI_API_KEY is not set. Check your .env file.")

# OpenAI WebSocket URL
url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
headers = [
    f"Authorization: Bearer {OPENAI_API_KEY}",
    "OpenAI-Beta: realtime=v1"
]

# 🎤 Audio Configuration
SAMPLE_RATE = 24000  # OpenAI uses 24kHz
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK = 1024  # Buffer size

# 🎤 Initialize PyAudio
p = pyaudio.PyAudio()

# 🎤 Open Mic Stream (Input)
mic_stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

# 🔊 Open Audio Playback Stream (Output)
audio_stream = p.open(format=FORMAT,
                      channels=CHANNELS,
                      rate=SAMPLE_RATE,
                      output=True)

def encode_audio_to_base64(audio_data):
    """Convert raw audio bytes to Base64-encoded PCM16 format."""
    return base64.b64encode(audio_data).decode("utf-8")

def send_audio(ws):
    """Continuously capture audio from mic and send to OpenAI."""
    while True:
        try:
            audio_chunk = mic_stream.read(CHUNK, exception_on_overflow=False)
            base64_chunk = encode_audio_to_base64(audio_chunk)

            event = {
                "type": "input_audio_buffer.append",
                "audio": base64_chunk
            }
            ws.send(json.dumps(event))
            print("🎤 Sent audio chunk to OpenAI")
        except Exception as e:
            print(f"❌ Error sending audio: {e}")

def on_open(ws):
    """Start audio streaming when WebSocket connects."""
    print("✅ Connected to OpenAI")

    # 🔄 Send setup event
    event = {
        "type": "session.update",
        "session": {
            "modalities": ["text", "audio"],
            "instructions": "Please assist the user.",
            "voice": "alloy",
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
        }
    }
    ws.send(json.dumps(event))
    print("📤 Sent session setup to OpenAI")

    # 🔄 Start streaming audio
    threading.Thread(target=send_audio, args=(ws,), daemon=True).start()

def on_message(ws, message):
    """Handle responses from OpenAI and play received audio."""
    data = json.loads(message)
    print("📩 Received response:", json.dumps(data, indent=2))

    if data.get("type") == "response.audio.delta" and "delta" in data:
        audio_bytes = base64.b64decode(data["delta"])
        audio_stream.write(audio_bytes)
        print("🎵 Playing received audio...")

ws = websocket.WebSocketApp(
    url,
    header=headers,
    on_open=on_open,
    on_message=on_message,
)

ws.run_forever()
