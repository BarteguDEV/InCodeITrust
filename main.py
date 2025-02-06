import firebase_admin
import json
from firebase_admin import credentials, db
import streamlit as st
import os
st.set_page_config(page_title="EldoGaming", page_icon="🎮", layout="wide")

st.logo("https://www.streamlit.io/images/brand/streamlit-mark-color.png")
pages = {
    "Home": [
        st.Page("Welcome.py", title="Welcome", icon="🏠")
    ],
    "Apps": [
        st.Page("EldoGaming.py", title="EldoGaming", icon="🎮")
    ],
    "Database": [
        st.Page("Supabase.py", title="Supabase", icon="🔗"),
    ]
}

pg = st.navigation(pages)
pg.run()