import streamlit as st
import datetime
import pandas as pd

# === Import the login and logout functions from auth.py ===
from auth import login, logout_button

# === Perform the login check immediately ===
login()

from voice.tts_engine import speak
from voice.stt_engine import listen
from core.document_indexer import search_knowledge_base
from core.config_manager import load_user_config, update_user_config
from utils.emergency import trigger_emergency
from core.reminder_manager import init_reminders, add_med_reminder, update_med_status, get_pending_reminders
from core.calendar_manager import init_calendar, add_calendar_event, get_events_for_date, update_event_status
from core.reminder_manager import load_reminders

# === Add viewport meta tag for mobile responsiveness ===
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
""", unsafe_allow_html=True)
# === Add viewport and PWA meta tags ===
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<link rel="manifest" href="/static/manifest.json">
<meta name="theme-color" content="#2196f3">
<script>
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/service-worker.js')
            .then(reg => console.log('Service Worker registered'))
            .catch(err => console.error('Service Worker registration failed:', err));
    }
</script>
""", unsafe_allow_html=True)

# === Load external CSS with dynamic font size ===
def load_css(file_path, font_size):
    with open(file_path) as f:
        css = f.read()
        # Inject dynamic font size
        css += f"\n:root {{ --font-size: {font_size}px; }}"
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# === Initialize calendar and reminders once ===
init_calendar()
init_reminders()

# === Load user preferences ===
user_config = load_user_config()
font_size = user_config["font_size"]
speech_rate = user_config["speech_rate"]
voice_type = user_config["voice_type"]

# Load CSS with initial font size
load_css("styles/main.css", font_size)

# === Initialize session state ===
st.session_state.setdefault("history", [])
st.session_state.setdefault("pending_emergency", False)
st.session_state.setdefault("conversation_context", {})
st.session_state.setdefault("med_reminders", [])
st.session_state.setdefault("todays_events", [])
st.session_state.setdefault("last_reload", datetime.datetime.now())

# === Refresh reminders and calendar with optimization ===
def reload_reminders_and_calendar():
    # Only reload if last reload was more than 60 seconds ago
    if (datetime.datetime.now() - st.session_state.last_reload).seconds > 60:
        try:
            # Load all reminders fresh from file
            reminders, next_id = load_reminders()
            st.session_state.med_reminders = reminders
            st.session_state.next_med_id = next_id
        except Exception:
            st.session_state.med_reminders = []
            st.session_state.next_med_id = 1

        try:
            today_str = datetime.date.today().strftime("%Y-%m-%d")
            st.session_state.todays_events = get_events_for_date(today_str) or []
        except Exception:
            st.session_state.todays_events = []

        st.session_state.last_reload = datetime.datetime.now()

reload_reminders_and_calendar()

# === Sidebar settings ===
with st.sidebar:
    st.header("🎛️ Personalize Your Experience")

    new_font_size = st.slider("Font Size", 12, 36, font_size, step=2)
    if new_font_size != font_size:
        update_user_config("font_size", new_font_size)
        load_css("styles/main.css", new_font_size)  # Reload CSS with new font size

    new_speech_rate = st.slider("Speech Rate", 0.5, 2.0, speech_rate, step=0.1)
    if new_speech_rate != speech_rate:
        update_user_config("speech_rate", new_speech_rate)

    new_voice_type = st.selectbox("Voice Type", ["default", "male", "female"],
                                  index=["default", "male", "female"].index(voice_type))
    if new_voice_type != voice_type:
        update_user_config("voice_type", new_voice_type)

    st.markdown("---")
    med_count = len([m for m in st.session_state.med_reminders if m["status"] == "pending"])
    event_count = len([e for e in st.session_state.todays_events if e.get("status") in ("pending", "upcoming")])

    st.markdown(f"""
        <div class='sidebar-stat'>
            🩺 Pending Medications: {med_count}<br>
            📅 Today's Events: {event_count}
        </div>
    """, unsafe_allow_html=True)

    if st.button("🚨 Trigger Emergency Now"):
        st.session_state.pending_emergency = True

    st.markdown("""
        <div class='sidebar-tip'>
        💡 Tip: Stay positive! Regular interaction helps your well-being.
        </div>
    """, unsafe_allow_html=True)

# === Main layout tabs ===
tabs = st.tabs(["Chat", "Medications", "Calendar"])

# === Chat Tab ===
with tabs[0]:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.title("👵 Elder Assistant (Prototype)")
    st.markdown("### 👋 How can I assist you today?")

    st.markdown('<div class="chat-history">', unsafe_allow_html=True)
    for entry in st.session_state.history:
        st.markdown(f"<div class='chat-message'><b>{entry['role']}:</b> {entry['text']}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    input_col, speak_col = st.columns([3, 1])  # Adjusted ratio for mobile

    with input_col:
        user_input = st.text_input("You:", "", key="chat_input", placeholder="Type your message here...")

    with speak_col:
        if st.button("🎤 Speak"):
            with st.spinner("Listening..."):
                spoken_text = listen()
                if spoken_text:
                    st.session_state.history.append({"role": "You", "text": spoken_text})
                    if "i need help" in spoken_text.lower():
                        st.session_state.pending_emergency = True
                    else:
                        response, ctx = search_knowledge_base(spoken_text, st.session_state.conversation_context)
                        st.session_state.conversation_context = ctx
                        st.session_state.history.append({"role": "Assistant", "text": response})
                        speak(response)
                        reload_reminders_and_calendar()

    if st.button("Send"):
        if user_input.strip():
            st.session_state.history.append({"role": "You", "text": user_input})
            if "i need help" in user_input.lower():
                st.session_state.pending_emergency = True
            else:
                response, ctx = search_knowledge_base(user_input, st.session_state.conversation_context)
                st.session_state.conversation_context = ctx
                st.session_state.history.append({"role": "Assistant", "text": response})
                speak(response)
                reload_reminders_and_calendar()

# === Medications Tab ===
with tabs[1]:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("## 💊 Medication Reminders")

    with st.form("add_reminder_form"):
        med_name = st.text_input("Medication Name", key="med_name")
        reminder_time = st.time_input("Reminder Time", value=datetime.time(9, 0), key="reminder_time")
        recurrence = st.selectbox("Repeat", ["none", "daily", "weekly"], key="recurrence")
        note = st.text_area("Notes (optional)", "", key="note")

        if st.form_submit_button("Add Reminder") and med_name.strip():
            add_med_reminder(
                med_name.strip(),
                reminder_time.strftime("%H:%M"),
                recurrence=recurrence,
                note=note.strip()
            )
            reload_reminders_and_calendar()
            st.success(f"Added reminder for {med_name} at {reminder_time.strftime('%H:%M')}")

    st.markdown("### 📋 All Reminders")
    if st.session_state.med_reminders:
        # Normalize reminder dicts
        reminders = []
        for r in st.session_state.med_reminders:
            reminders.append({
                "ID": r["id"],
                "Medication": r["med_name"],
                "Time": r["time"],
                "Repeat": r.get("recurrence", "none"),
                "Notes": r.get("note", ""),
                "Status": r["status"],
                "Last Updated": r.get("timestamp", "—")
            })

        df = pd.DataFrame(reminders)
        df.set_index("ID", inplace=True)
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "Medication": st.column_config.TextColumn(width="medium"),
                "Time": st.column_config.TextColumn(width="small"),
                "Status": st.column_config.TextColumn(width="small"),
                "Repeat": st.column_config.TextColumn(width="small"),
                "Notes": st.column_config.TextColumn(width="large"),
                "Last Updated": st.column_config.TextColumn(width="medium")
            }
        )
    else:
        st.info("No medication reminders set yet.")

# === Calendar Tab ===
with tabs[2]:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("## 📅 Calendar Reminders")

    with st.form("add_calendar_event_form"):
        title = st.text_input("Event Title", key="event_title")
        date = st.date_input("Event Date", value=datetime.date.today(), key="event_date")
        time = st.time_input("Event Time", value=datetime.datetime.now().time(), key="event_time")
        if st.form_submit_button("Add Event") and title.strip():
            add_calendar_event(title.strip(), date.strftime("%Y-%m-%d"), time.strftime("%H:%M"))
            reload_reminders_and_calendar()
            st.success(f"Added event '{title}' on {date} at {time.strftime('%H:%M')}")

    if st.session_state.todays_events:
        st.markdown('<ul class="event-list">', unsafe_allow_html=True)
        for e in st.session_state.todays_events:
            badge = f"<span class='status-pill status-{e['status']}'>{e['status'].capitalize()}</span>"
            datetime_str = e.get("datetime", f"{e['date']} {e['time']}")
            display_time = datetime_str[11:16] if len(datetime_str) >= 16 else e["time"]
            st.markdown(f"<li><b>{e['title']}</b> at {display_time} {badge}</li>", unsafe_allow_html=True)
        st.markdown('</ul>', unsafe_allow_html=True)
    else:
        st.info("No calendar events scheduled for today.")

# === Emergency confirmation ===
if st.session_state.pending_emergency:
    st.warning("🚨 Do you really want to trigger an emergency alert?")
    col1, col2 = st.columns([1, 1])  # Equal ratio for mobile
    with col1:
        if st.button("Yes, I need help!"):
            message = trigger_emergency()
            st.session_state.history.append({"role": "System", "text": message})
            speak("Emergency alert triggered. Help is on the way.")
            st.session_state.pending_emergency = False
    with col2:
        if st.button("Cancel"):
            st.session_state.pending_emergency = False
            st.success("Emergency alert canceled.")