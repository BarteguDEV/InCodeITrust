import streamlit as st

st.title("Hello world!")
st.code("Coding in progress...")


def page_2():
    st.title("Page 2")

pg = st.navigation([st.Page("page_1.py"), st.Page(page_2)])
pg.run()