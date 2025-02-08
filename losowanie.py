import streamlit as st
import random

st.title("🎲 Losowanie pozycji w barze")
st.caption("Piwo, wódka, czy może jednak cola?")

# Pobieranie zakresu od użytkownika
min_val = st.number_input("Podaj pierwszą liczbę:", value=1, step=1)
max_val = st.number_input("Podaj drugą liczbę:", value=10, step=1)

# Zapewnienie, że min_val < max_val
if min_val >= max_val:
    st.error("Druga liczba musi być większa niż pierwsza!")

# Losowanie liczby
if st.button("Losuj liczbę!"):
    random_number = random.randint(int(min_val), int(max_val))
    st.success(f"🎉 Wylosowana liczba: {random_number}")
