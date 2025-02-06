import streamlit as st
st.set_page_config(page_title="EldoGaming", page_icon="🎮", layout="wide")

# Strona boczna do logowania
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# Wprowadzenie hasła w sidebarze
if not st.session_state.admin_logged_in:
    with st.sidebar:
        admin_pass = st.text_input("Admin password", type="password")
        
        if admin_pass == st.secrets["barteguapp"]["secret_pass"]:
            st.session_state.admin_logged_in = True
            st.success("Hasło poprawne. Możesz uzyskać dostęp do zakładki 'Database'.")

# Definicja stron
pages = {
    "Home": [
        st.Page("Welcome.py", title="Welcome", icon="🏠")
    ],
    "Apps": [
        st.Page("EldoGaming.py", title="EldoGaming", icon="🎮")
    ]
}

# Jeśli hasło jest poprawne, dodajemy zakładkę "Database"
if st.session_state.admin_logged_in:
    pages["Database"] = [
        st.Page("Supabase.py", title="Supabase", icon="🔗")
    ]

# Nawigacja
pg = st.navigation(pages)
pg.run()