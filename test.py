import pyaudio
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000  # Your system supports 48kHz

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording for 3 seconds...")

frames = []
for _ in range(0, int(RATE / CHUNK * 3)):
    data = stream.read(CHUNK, exception_on_overflow=False)  # Prevents buffer overflow
    frames.append(data)

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

# Save the recorded audio to a file
wf = wave.open("test.wav", "wb")
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b"".join(frames))
wf.close()
