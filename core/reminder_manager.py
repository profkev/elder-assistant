import streamlit as st
import datetime
import json
import os

REMINDER_FILE = "data/med_reminders.json"

def load_reminders():
    if not os.path.exists(REMINDER_FILE):
        return [], 1
    try:
        with open(REMINDER_FILE, "r") as f:
            data = json.load(f)
            reminders = data.get("reminders", [])
            next_id = data.get("next_id", 1)
            return reminders, next_id
    except Exception as e:
        print(f"Error loading reminders: {e}")
        return [], 1

def save_reminders(reminders, next_id):
    try:
        with open(REMINDER_FILE, "w") as f:
            json.dump({"reminders": reminders, "next_id": next_id}, f, indent=2)
    except Exception as e:
        print(f"Error saving reminders: {e}")

def init_reminders():
    if "med_reminders" not in st.session_state or "next_med_id" not in st.session_state:
        reminders, next_id = load_reminders()
        st.session_state.med_reminders = reminders
        st.session_state.next_med_id = next_id

def add_med_reminder(med_name: str, time_str: str, recurrence: str = "none", note: str = ""):
    reminder = {
        "id": st.session_state.next_med_id,
        "med_name": med_name,
        "time": time_str,
        "recurrence": recurrence,
        "note": note,
        "status": "pending",
        "timestamp": None,
    }
    st.session_state.med_reminders.append(reminder)
    st.session_state.next_med_id += 1
    save_reminders(st.session_state.med_reminders, st.session_state.next_med_id)

def update_med_status(reminder_id: int, status: str):
    for rem in st.session_state.med_reminders:
        if rem["id"] == reminder_id:
            rem["status"] = status
            rem["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            break
    save_reminders(st.session_state.med_reminders, st.session_state.next_med_id)

def get_pending_reminders(current_time: str, window_minutes: int = 2):
    try:
        now = datetime.datetime.strptime(current_time, "%H:%M")
    except Exception as e:
        print(f"Error parsing current_time: {e}")
        return []

    pending = []
    for rem in st.session_state.med_reminders:
        if rem["status"] == "pending":
            try:
                rem_time = datetime.datetime.strptime(rem["time"], "%H:%M")
                delta_minutes = abs((now - rem_time).total_seconds() / 60)
                if delta_minutes <= window_minutes:
                    pending.append(rem)
            except Exception as e:
                print(f"Error parsing reminder time '{rem['time']}': {e}")
    return pending
