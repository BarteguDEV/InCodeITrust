import streamlit as st
import geocoder

# Funkcja do pobierania lokalizacji użytkownika
def get_location():
    g = geocoder.ip('me')  # Pobiera lokalizację na podstawie IP
    if g.ok:
        return g.latlng  # Zwraca szerokość i długość geograficzną
    else:
        st.error("Nie udało się pobrać lokalizacji.")
        return None

# Dodanie zgody na pobranie lokalizacji
st.title("Pobierz lokalizację użytkownika")
st.write("Aby uzyskać dokładną lokalizację, musisz wyrazić zgodę.")

if st.button("Pobierz lokalizację"):
    location = get_location()
    
    if location:
        lat, lon = location
        st.write(f"Twoja lokalizacja: Latitude = {lat}, Longitude = {lon}")
        
        # Wyświetlanie mapy z lokalizacją
        st.map([{"lat": lat, "lon": lon}])
