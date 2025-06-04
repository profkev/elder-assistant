import streamlit as st
import hashlib

def hash_password(password):
    return hashlib.sha256(password.strip().encode('utf-8')).hexdigest()

# Set the correct SHA-256 hash for 'Secure@1234'
CORRECT_HASHED_PASSWORD = "7d8c909eadd8817cc2a3f327240b9c7122c88a986fda03f88d641f2c037537a6"

def login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("🔒 Secure Login")
        password = st.text_input("Enter Password", type="password")

        if st.button("Login"):
            if hash_password(password) == CORRECT_HASHED_PASSWORD:
                st.session_state.logged_in = True
                st.success(" Login successful!")
                st.rerun()  
            else:
                st.error(" Incorrect password. Please try again.")
        st.stop()  # Only stop if NOT logged in

def logout_button():
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
