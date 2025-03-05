import asyncio
import websockets
import json
import pyaudio
import base64

# OpenAI API Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_WS_URL = "wss://api.openai.com/v1/realtime"

# Audio Configuration
CHUNK = 1024  # Audio buffer size
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000  # Whisper API prefers 16kHz

# Initialize PyAudio
audio = pyaudio.PyAudio()

def get_microphone_stream():
    return audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,# Use your built-in mic
        frames_per_buffer=CHUNK
    )

async def stream_audio():
    """Streams microphone input to OpenAI's Realtime API"""
    async with websockets.connect(
        OPENAI_WS_URL,
        extra_headers={"Authorization": f"Bearer {OPENAI_API_KEY}"}
    ) as websocket:
        print("🔗 Connected to OpenAI Realtime API")

        mic_stream = get_microphone_stream()

        try:
            while True:
                audio_data = mic_stream.read(CHUNK)
                encoded_audio = base64.b64encode(audio_data).decode("utf-8")

                await websocket.send(json.dumps({
                    "type": "input_audio",
                    "audio": encoded_audio
                }))

                response = await websocket.recv()
                response_data = json.loads(response)

                if "text" in response_data:
                    ai_response = response_data["text"]
                    print(f"🗣️ AI: {ai_response}")

                    if ai_response.startswith("CMD:"):
                        command = ai_response[4:].strip()
                        execute_command(command)

        except KeyboardInterrupt:
            print("\n🛑 Stopping CyberCore...")
        finally:
            mic_stream.stop_stream()
            mic_stream.close()
            audio.terminate()

async def execute_command(command):
    """Execute CLI commands received from OpenAI"""
    import subprocess
    try:
        print(f"⚡ Executing: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(f"✅ Output:\n{result.stdout}")
    except Exception as e:
        print(f"❌ Error executing command: {str(e)}")

if __name__ == "__main__":
    asyncio.run(stream_audio())
