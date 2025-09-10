import time
import os
import sounddevice as sd
import numpy as np
import speech_recognition as sr
#import pyttsx3
from gtts import gTTS
import wave
import pyglet


# 🔊 Speak the text using pyttsx3 TTS
def speak_text(text):
    tts = gTTS(text=text, lang='en')
    tts.save("tts_output.mp3")
    music = pyglet.media.load("tts_output.mp3", streaming=False)
    music.play()
    time.sleep(music.duration)
    os.remove("tts_output.mp3")

# 🎧 Record system audio dynamically using silence detection
def record_system_audio(filename="copilot_response.wav", silence_threshold=200, max_silence_after_voice=3):
    fs = 44100  # Sample rate
    channels = 2  # Stereo
    block_size = 1024
    print("🎧 Waiting for Copilot to speak...")
    recording = []
    silence_start_time = None
    voice_started = False
    start_time = time.time()

    try:
        with sd.InputStream(samplerate=fs, channels=channels, dtype='int16', blocksize=block_size) as stream:
            while True:
                block, _ = stream.read(block_size)
                volume_norm = np.linalg.norm(block)
                recording.append(block)
                if volume_norm > silence_threshold:
                    if not voice_started:
                        print("🟢 Voice detected! Starting full recording...")
                        voice_started = True
                    silence_start_time = None
                else:
                    if voice_started:
                        if silence_start_time is None:
                            silence_start_time = time.time()
                        elif time.time() - silence_start_time > max_silence_after_voice:
                            print("🛑 Detected silence. Stopping recording...")
                            break
    except Exception as e:
        print(f"❌ Error during recording: {e}")
        return False

    if voice_started:
        audio_data = np.concatenate(recording)
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes(audio_data.tobytes())
        print("✅ Recording complete.")
        print(f"⏱️ Total time: {round(time.time() - start_time, 2)}s")
        return True
    else:
        print("⚠️ No voice detected. Skipping save.")
        return False

# 🧠 Transcribe recorded audio to text using Google STT
def transcribe_audio_file(filepath):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(filepath) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio, language="en-EN")  # Change Language from here ---- for hindi hi-HI
    except sr.UnknownValueError:
        return "❌ Could not understand audio"
    except sr.RequestError as e:
        return f"⚠️ API Error: {e}"
    except Exception as e:
        return f"⚠️ File Error: {e}"