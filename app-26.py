
import streamlit as st
import requests
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Fester Token & Host – NICHT sichtbar für Benutzer
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

st.set_page_config(page_title="UniFi Verwaltung", page_icon="🛡️")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "view" not in st.session_state:
    st.session_state.view = None

# Login-Bereich
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

# Navigation nach Login
st.sidebar.title("🧭 Navigation")
if st.sidebar.button("➕ Benutzer anlegen"):
    st.session_state.view = "create"
if st.sidebar.button("🪪 Karte anlernen"):
    st.session_state.view = "nfc"
if st.sidebar.button("✏️ Benutzer ändern / löschen"):
    st.session_state.view = "edit"
if st.sidebar.button("🚪 Logout"):
    st.session_state.clear()
    st.rerun()

# Funktionsbausteine
def list_users():
    res = requests.get(f"{BASE_URL}/users", headers=HEADERS, verify=False)
    return res.json().get("data", []) if res.status_code == 200 else []

def assign_pin(user_id, pin_code):
    payload = { "pin_code": pin_code }
    return requests.put(f"{BASE_URL}/users/{user_id}/pin_codes", headers=HEADERS, json=payload, verify=False)

def assign_nfc_card(user_id, token):
    payload = {"token": token, "force_add": True}
    return requests.put(f"{BASE_URL}/users/{user_id}/nfc_cards", headers=HEADERS, json=payload, verify=False)

def start_nfc_session(device_id):
    res = requests.post(f"{BASE_URL}/credentials/nfc_cards/sessions", headers=HEADERS, json={"device_id": device_id}, verify=False)
    return res.json().get("data", {}).get("session_id")

def get_token_from_session(session_id):
    res = requests.get(f"{BASE_URL}/nfc_cards/sessions/{session_id}", headers=HEADERS, verify=False)
    return res.json().get("data", {}).get("token")

def render_user_create():
    st.header("➕ Neuen Benutzer anlegen")
    with st.form("create_user"):
        fn = st.text_input("Vorname")
        ln = st.text_input("Nachname")
        em = st.text_input("E-Mail")
        kfz = st.text_input("KFZ-Kennzeichen")
        pin = st.text_input("PIN (4-stellig)")
        submit = st.form_submit_button("Benutzer anlegen")

        if submit:
            payload = {
                "first_name": fn,
                "last_name": ln
            }
            if em and "@" in em and "." in em:
                payload["user_email"] = em
            if kfz:
                payload["employee_number"] = kfz
            r = requests.post(f"{BASE_URL}/users", headers=HEADERS, json=payload, verify=False)
            if r.status_code == 200:
                response_data = r.json()
                if r.status_code == 200 and "data" in response_data:
                    user_id = response_data["data"]["id"]
                    assign_pin(user_id, pin)
                    st.success(f"✅ Benutzer {fn} {ln} angelegt")
                else:
                    st.error("❌ Fehler bei der Benutzeranlage.")
                    if "msg" in response_data:
                        st.warning(f"💬 Servermeldung: {response_data['msg']}")
                    st.code(r.text)
            else:
                st.error("❌ Fehler bei der Benutzeranlage.")

def render_nfc():
    st.header("🪪 Karte zuweisen")
    users = list_users()
    if not users:
        st.info("Keine Benutzer gefunden.")
        return
    selected = st.selectbox("Benutzer wählen", [f"{u['first_name']} {u['last_name']}" for u in users])
    user = users[[f"{u['first_name']} {u['last_name']}" for u in users].index(selected)]
    user_id = user["id"]

    devices = requests.get(f"{BASE_URL}/devices", headers=HEADERS, verify=False).json().get("data", [])
    if isinstance(devices[0], list): devices = devices[0]
    reader_map = {f"{d['name']} ({d['type']})": d["id"] for d in devices}
    reader = st.selectbox("Leser auswählen", list(reader_map.keys()))
    reader_id = reader_map[reader]

    if st.button("📶 Karte scannen & zuweisen"):
        st.info("Starte NFC-Session … bitte Karte scannen.")
        start_res = requests.post(
            f"{BASE_URL}/api/v1/developer/credentials/nfc_cards/sessions",
            headers={**headers, "Content-Type": "application/json"},
            json={"device_id": DEVICE_ID, "reset_ua_card": False},
            verify=False
        )
        if start_res.status_code != 200:
            st.error(f"Fehler beim Starten: {start_res.status_code}")
            st.code(start_res.text)
            st.stop()

        session_id = start_res.json().get("data", {}).get("session_id")
        st.write(f"Session-ID: {session_id}")

        token = None
        for _ in range(20):
            check = requests.get(
                f"{BASE_URL}/api/v1/developer/credentials/nfc_cards/sessions/{session_id}",
                headers=headers,
                verify=False
            )
            data = check.json().get("data")
            if data and "token" in data:
                token = data["token"]
                card_id = data.get("card_id", "")
                break
            time.sleep(1)

        if token:
            st.success(f"✅ Karte erkannt – Token: {token}")
            assign = requests.put(
                f"{BASE_URL}/api/v1/developer/users/{st.session_state.new_user_id}/nfc_cards",
                headers={**headers, "Content-Type": "application/json"},
                json={"token": token, "force_add": True},
                verify=False
            )
            if assign.status_code == 200:
                st.success(f"Karte wurde {st.session_state.new_user_name} zugewiesen.")
            else:
                st.error(f"Zuweisung fehlgeschlagen: {assign.status_code}")
                st.code(assign.text)
        else:
            st.error("❌ Keine Karte erkannt.")
def render_user_edit():
    st.header("✏️ Benutzer ändern / löschen")
    users = list_users()
    if not users:
        st.info("Keine Benutzer vorhanden.")
        return
    selected = st.selectbox("Benutzer wählen", [f"{u['first_name']} {u['last_name']}" for u in users])
    user = users[[f"{u['first_name']} {u['last_name']}" for u in users].index(selected)]

    with st.form("edit_user"):
        fn = st.text_input("Vorname", value=user["first_name"])
        ln = st.text_input("Nachname", value=user["last_name"])
        em = st.text_input("E-Mail", value=user["user_email"])
        kfz = st.text_input("KFZ-Kennzeichen", value=user["employee_number"])
        pin = st.text_input("Neue PIN (optional)", type="password")
        submit = st.form_submit_button("Änderung speichern")

    if submit:
        payload = {
            "first_name": fn,
            "last_name": ln,
            "user_email": em,
            "employee_number": kfz
        }
        u = requests.put(f"{BASE_URL}/users/{user['id']}", headers=HEADERS, json=payload, verify=False)
        if u.status_code == 200:
            if pin:
                assign_pin(user["id"], pin)
            st.success("✅ Benutzer aktualisiert.")
        else:
            st.error("❌ Fehler bei Änderung.")

    if st.button("🗑️ Benutzer löschen"):
        requests.put(f"{BASE_URL}/users/{user['id']}", headers=HEADERS, json={"status": "DEACTIVATED"}, verify=False)
        d = requests.delete(f"{BASE_URL}/users/{user['id']}", headers=HEADERS, verify=False)
        if d.status_code == 200:
            st.success("🗑️ Benutzer gelöscht.")
            st.rerun()
        else:
            st.error("Fehler beim Löschen.")
            headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}

# Auswahl-Ansicht laden
if st.session_state.view == "create":
    render_user_create()
elif st.session_state.view == "nfc":
    render_nfc()
elif st.session_state.view == "edit":
    render_user_edit()
else:
    st.markdown("⬅️ Bitte wähle links eine Funktion aus.")
