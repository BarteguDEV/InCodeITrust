import streamlit as st
import pandas as pd
st.set_page_config(layout="wide")
st.title("Wyjscia melanze")

person = st.selectbox(
    "Wybierz osobe",
    ("Bartek", "Maciek", "Bacper"),
)

option = st.selectbox(
    "Wybierz miejscowke",
    ("SKUNSTREFA", "PIZZA", "KFC"),
)

c1,c2,c3 = st.columns([0.5,0.5,3,])
with c1:
    st.caption(f":green-background[Oceny dla {person} z {option}]")
    st.code("2")
with c2:
    st.caption(f"Oceny dla {person} z {option}")
    st.code("2")
with c3:    
    st.caption(f"Oceny dla {person} z {option}")
    st.code("3")
st.subheader(f"Oceny dla {person} z {option}")
st.code("14")
st.subheader(f"Oceny dla {person} z {option}")
st.code("5")
st.subheader(f"Oceny dla {person} z {option}")
st.code("1")
st.subheader(f"Oceny dla {person} z {option}")
st.code("1")
# Przykładowe dane
# df = pd.DataFrame({
#     "OCENIAJĄCY": ["Jan", "Anna"],
#     "FOOD": [5, 4],
#     "WYSTRÓJ": [4, 3],
#     "OBSŁUGA": [5, 4],
#     "PERFORMANCE PER PRICE": [3, 4],
#     "INNE": [4, 5],
#     "ŚREDNIA Z PUNKTÓW": [4.2, 4.0],
#     "ŚREDNIA Z MIEJSCÓWKI": [4.1, 3.9],
#     "KOMENTARZ": ["Bardzo dobre", "Średnie"]
# })

# # Zamiana kolumn na wiersze
# df_melted = df.melt(var_name="KATEGORIA", value_name="WARTOŚĆ")

# # Dodanie numeracji
# df_melted.insert(0, "LP", range(1, len(df_melted) + 1))

# df_melted["MIEJSCE"] = option
# st.dataframe(df_melted,hide_index=True, width=500, height=500)

# st.bar_chart(df["INNE"])
# st.text_area("Komentarz", "Napisz coś")