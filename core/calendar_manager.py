import os
import json
from datetime import datetime

CALENDAR_FILE = "data/calendar_events.json"

def load_calendar_events():
    if not os.path.exists(CALENDAR_FILE):
        return [], 1
    try:
        with open(CALENDAR_FILE, "r") as f:
            data = json.load(f)
            return data.get("events", []), data.get("next_id", 1)
    except Exception as e:
        print(f"Error loading calendar: {e}")
        return [], 1

def save_calendar_events(events, next_id):
    try:
        with open(CALENDAR_FILE, "w") as f:
            json.dump({"events": events, "next_id": next_id}, f, indent=2)
    except Exception as e:
        print(f"Error saving calendar: {e}")

def init_calendar():
    import streamlit as st
    if "calendar_events" not in st.session_state or "next_event_id" not in st.session_state:
        events, next_id = load_calendar_events()
        st.session_state.calendar_events = events
        st.session_state.next_event_id = next_id

def add_calendar_event(title: str, date: str, time: str):
    import streamlit as st
    try:
        dt_obj = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        full_datetime = dt_obj.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        full_datetime = f"{date} {time}"  # fallback

    event = {
        "id": st.session_state.next_event_id,
        "title": title,
        "date": date,            # e.g. "2025-05-28"
        "time": time,            # e.g. "14:30"
        "datetime": full_datetime,  # e.g. "2025-05-28 14:30"
        "status": "upcoming"
    }
    st.session_state.calendar_events.append(event)
    st.session_state.next_event_id += 1
    save_calendar_events(st.session_state.calendar_events, st.session_state.next_event_id)

def get_events_for_date(date_str: str):
    import streamlit as st
    return [event for event in st.session_state.calendar_events if event["date"] == date_str]

def update_event_status(event_id: int, status: str):
    import streamlit as st
    for event in st.session_state.calendar_events:
        if event["id"] == event_id:
            event["status"] = status
            break
    save_calendar_events(st.session_state.calendar_events, st.session_state.next_event_id)
