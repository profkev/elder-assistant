import queue
import sounddevice as sd
import vosk
import json
import os
import time

MODEL_PATH = "models/vosk-model-small-en-us-0.15"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Vosk model not found at {MODEL_PATH}")

model = vosk.Model(MODEL_PATH)
q = queue.Queue()

def callback(indata, frames, time_, status):
    if status:
        print(f"Audio status: {status}")
    q.put(bytes(indata))

def listen(timeout=10):
    """Record from mic and return transcribed text (blocking)."""
    try:
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                               channels=1, callback=callback):
            rec = vosk.KaldiRecognizer(model, 16000)
            print("Listening... Speak now.")
            start_time = time.time()

            while True:
                if time.time() - start_time > timeout:
                    print("⏱️ Timeout reached.")
                    return "Listening timed out."

                data = q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "")
                    print(f"You said: {text}")
                    return text.strip().lower()
    except Exception as e:
        print(f"Microphone error: {e}")
        return "Sorry, I couldn't hear you."
