import streamlit as st

st.title("Hello world!")
st.code("Coding in progress...")

st.logo("https://www.streamlit.io/images/brand/streamlit-mark-color.png")
pages = {
    "Home": [
        st.Page("Welcome.py", title="Welcome",icon="🏠"),
    ],
    "Your account": [
        st.Page("create_account.py", title="Create your account"),
        st.Page("manage_account.py", title="Manage your account"),
    ]
}

pg = st.navigation(pages)
pg.run()