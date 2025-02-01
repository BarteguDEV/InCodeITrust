import streamlit as st
import pandas as pd

# Add custom CSS to hide the GitHub icon
hide_github_icon = """
#GithubIcon {
  visibility: hidden;
}
"""
st.markdown(hide_github_icon, unsafe_allow_html=True)

st.title("Wyjscia melanze")

df = pd.DataFrame({"MIEJSCE": [], "OCENIAJĄCY": []})

st.data_editor(data=df, key="data_editor")

if st.button("Click me"):
    st.success("You clicked me!")
