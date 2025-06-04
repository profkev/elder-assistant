import json
import os

CONFIG_PATH = os.path.join("data", "config.json")

def load_user_config():
    if not os.path.exists(CONFIG_PATH):
        return {
            "font_size": 24,
            "speech_rate": 1.0,
            "voice_type": "default"
        }
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_user_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def update_user_config(key, value):
    config = load_user_config()
    config[key] = value
    save_user_config(config)
