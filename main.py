import firebase_admin
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

# Sprawdzenie, czy aplikacja Firebase została już zainicjowana
if not firebase_admin._apps:
    # Ścieżka do lokalnego pliku JSON z kluczem serwisowym
    sciezka_do_klucza = "V:/python-streamlit/streamlit-firebase.json"

    # Inicjalizacja aplikacji Firebase
    cred = credentials.Certificate(sciezka_do_klucza)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://streamlit-bg-default-rtdb.europe-west1.firebasedatabase.app/'
    })

pg = st.navigation(pages)
pg.run()