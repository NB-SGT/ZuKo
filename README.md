# UniFi Benutzerverwaltung (Streamlit App)

Dies ist eine moderne, webbasierte Benutzerverwaltungs-App für UniFi Access Systeme.  
Sie basiert auf Python + Streamlit und ist für die Veröffentlichung auf **Streamlit Cloud** vorbereitet.

## 🧩 Funktionen

- Benutzer anlegen (mit PIN & KFZ)
- Login-geschützte Oberfläche
- Modernes, responsives Layout
- API-Zugriff auf UniFi-Controller

## 🚀 Deployment (Streamlit Cloud)

1. Repository auf GitHub hochladen
2. Gehe zu https://streamlit.io/cloud
3. Neues App-Deployment starten
4. `app.py` als Startdatei auswählen
5. `requirements.txt` wird automatisch installiert

## 🛠️ Lokaler Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## ⚠️ Hinweise

- Die API-Zugangsdaten sind fest in `app.py` hinterlegt. Diese sollten bei öffentlichem Deployment abgesichert werden (z. B. per `.streamlit/secrets.toml` oder Umgebungsvariablen).
