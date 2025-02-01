import streamlit as st
import pandas as pd
st.set_page_config(layout="wide")
st.title("Wyjscia melanze")

option = st.selectbox(
    "Wybierz miejscowke",
    ("SKUNSTREFA", "PIZZA", "KFC"),
)
# Przykładowe dane
df = pd.DataFrame({
    "MIEJSCE": ["Restauracja A", "Restauracja B"],
    "OCENIAJĄCY": ["Jan", "Anna"],
    "FOOD": [5, 4],
    "WYSTRÓJ": [4, 3],
    "OBSŁUGA": [5, 4],
    "PERFORMANCE PER PRICE": [3, 4],
    "INNE": [4, 5],
    "ŚREDNIA Z PUNKTÓW": [4.2, 4.0],
    "ŚREDNIA Z MIEJSCÓWKI": [4.1, 3.9],
    "KOMENTARZ": ["Bardzo dobre", "Średnie"]
})

# Zamiana kolumn na wiersze
df_melted = df.melt(var_name="KATEGORIA", value_name="WARTOŚĆ")

# Dodanie numeracji
df_melted.insert(0, "LP", range(1, len(df_melted) + 1))

df_melted["MIEJSCE"] = option
st.dataframe(df_melted,hide_index=True, width=500, height=500)

st.bar_chart(df["INNE"])