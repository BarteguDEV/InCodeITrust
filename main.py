import firebase_admin
import json
from firebase_admin import credentials, db
import streamlit as st

st.logo("https://www.streamlit.io/images/brand/streamlit-mark-color.png")
pages = {
    "Home": [
        st.Page("Welcome.py", title="Welcome", icon="🏠")
    ],
    "Apps": [
        st.Page("EldoGaming.py", title="EldoGaming", icon="🎮")
    ],
    "Database": [
        st.Page("Managment.py", title="Managment", icon="⚙️")
    ]
}

# Inicjalizacja Firebase (tylko raz)
if not firebase_admin._apps:
    firebase_config = st.secrets["firebase"]
    # Konwersja stringa JSON do słownika
    try:
        service_account_info = json.loads(firebase_config["service_account_key"])
    except json.JSONDecodeError as e:
        st.error(f"❌ Błąd dekodowania JSON: {e}")
        st.stop()

    cred = credentials.Certificate(service_account_info)

    firebase_admin.initialize_app(cred, {
        'databaseURL': firebase_config["database_url"]
    })


pg = st.navigation(pages)
pg.run()