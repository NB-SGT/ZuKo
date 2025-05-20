
import streamlit as st
import requests
from PIL import Image
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.set_page_config(page_title="UniFi Verwaltung", page_icon="🛡️", layout="wide")

API_TOKEN = "QS5JL7IR7qcSwG5JMnXM2A"
BASE_URL = "https://192.168.1.1:12445/api/v1/developer"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}
USER_CREDENTIALS = {
    "NB": "Start123",
    "admin": "passwort123"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "view" not in st.session_state:
    st.session_state.view = None

st.markdown("<h2>🛡️ UniFi Benutzerverwaltung</h2>", unsafe_allow_html=True)

if not st.session_state.logged_in:
    st.title("🔐 Anmeldung")
    with st.form("login_form"):
        user = st.text_input("Benutzer")
        pwd = st.text_input("Passwort", type="password")
        submit = st.form_submit_button("Anmelden")
        if submit:
            if user in USER_CREDENTIALS and USER_CREDENTIALS[user] == pwd:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.success(f"Willkommen {user}!")
                st.rerun()
            else:
                st.error("❌ Falsche Zugangsdaten")
    st.stop()

st.sidebar.title("🧭 Navigation")
if st.sidebar.button("➕ Benutzer anlegen"):
    st.session_state.view = "create"
if st.sidebar.button("🚪 Logout"):
    st.session_state.clear()
    st.rerun()

def render_user_create():
    st.header("➕ Neuen Benutzer anlegen")
    with st.form("create_user"):
        fn = st.text_input("Vorname")
        ln = st.text_input("Nachname")
        em = st.text_input("E-Mail")
        kfz = st.text_input("KFZ-Kennzeichen")
        pin = st.text_input("PIN (4-stellig)", type="password")
        submit = st.form_submit_button("Benutzer anlegen")
        if submit:
            st.success(f"✅ Benutzer {fn} {ln} wurde (scheinbar) angelegt.")

if st.session_state.view == "create":
    render_user_create()
else:
    st.markdown("⬅️ Bitte wähle links eine Funktion aus.")
