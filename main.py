import firebase_admin
import json
from firebase_admin import credentials, db
import streamlit as st

st.logo("https://www.streamlit.io/images/brand/streamlit-mark-color.png")
pages = {
    "Home": [
        st.Page("Welcome.py", title="Welcome",icon="🏠")
    ],
    "Apps": [
        st.Page("EldoGaming.py", title="EldoGaming")
    ],
    "Database": [
        st.Page("Managment.py", title="Managment", icon="⚙️")
    ]
}

# Inicjalizacja Firebase (tylko raz)
if not firebase_admin._apps:
    # Pobierz konfigurację Firebase z secrets.toml
    firebase_config = st.secrets["firebase"]
    
    # Konwertuj zawartość service_account_key (która jest zapisana jako string) na słownik
    service_account_info = json.loads(firebase_config["service_account_key"])
    
    # Inicjalizacja poświadczeń
    cred = credentials.Certificate(service_account_info)
    
    # Inicjalizacja Firebase z pobranym URL bazy danych
    firebase_admin.initialize_app(cred, {
        'databaseURL': firebase_config["database_url"]
    })

pg = st.navigation(pages)
pg.run()