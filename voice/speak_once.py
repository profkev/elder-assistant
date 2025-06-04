

import sys
import os
import pyttsx3


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, project_root)

from core.config_manager import load_user_config


import sys
import pyttsx3
from core.config_manager import load_user_config

# Get text to speak
if len(sys.argv) < 2:
    print("No text provided.")
    sys.exit(1)

text = sys.argv[1]

# Load user config
user_config = load_user_config()
engine = pyttsx3.init()
engine.setProperty('rate', user_config["speech_rate"] * 150)

voices = engine.getProperty('voices')
if user_config["voice_type"] == "male":
    engine.setProperty('voice', voices[0].id)
elif user_config["voice_type"] == "female" and len(voices) > 1:
    engine.setProperty('voice', voices[1].id)
else:
    engine.setProperty('voice', voices[0].id)

engine.say(text)
engine.runAndWait()
