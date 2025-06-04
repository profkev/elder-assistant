import datetime
import os

LOG_PATH = os.path.join("data", "emergency_log.txt")

def trigger_emergency(user="User"):
    """Logs an emergency event. In future, can notify via SMS/email."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] 🚨 Emergency triggered by {user}\n"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(message)
    return message
