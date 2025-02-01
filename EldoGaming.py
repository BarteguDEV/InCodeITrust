import streamlit as st
import pandas as pd

st.title("Wyjscia melanze")

df = pd.DataFrame({"MIEJSCE": [], "OCENIAJĄCY": []})

st.data_editor(data=df, key="data_editor")

if st.button("Click me"):
    st.success("You clicked me!")
