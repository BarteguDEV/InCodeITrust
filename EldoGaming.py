import streamlit as st
import pandas as pd
st.set_page_config(layout="wide")
st.title("Wyjscia melanze")

df = pd.DataFrame({"MIEJSCE": [], "OCENIAJĄCY": [],
                   "FOOD":[],
                   "WYSTRÓJ":[],
                   "OBSŁUGA":[],
                   "PERFORMANCE PER PRICE":[],
                   "INNE":[],
                   "ŚREDNIA Z PUNKTÓW":[],
                   "ŚREDNIA Z MIEJSCÓWKI":[],
                   "KOMENTARZ":[]})

st.data_editor(data=df, key="data_editor",num_rows="dynamic")

if st.button("Click me"):
    st.success("You clicked me!")
