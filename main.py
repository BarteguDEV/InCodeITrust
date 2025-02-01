import streamlit as st

st.logo("https://www.streamlit.io/images/brand/streamlit-mark-color.png")
pages = {
    "Home": [
        st.Page("Welcome.py", title="Welcome",icon="🏠"),
    ],
    "Your account": [
        st.Page("create_account.py", title="Create your account"),
        st.Page("manage_account.py", title="Manage your account"),
        st.Page("EldoGaming.py", title="EldoGaming"),
    ]
}

pg = st.navigation(pages)
pg.run()