import subprocess
import os
import shlex
import sys

def speak(text):
    safe_text = shlex.quote(text)
    script_path = os.path.join(os.path.dirname(__file__), "speak_once.py")
    python_executable = sys.executable  

    try:
        subprocess.Popen([python_executable, script_path, safe_text])
    except Exception as e:
        print(f"[TTS ERROR]: {e}")
