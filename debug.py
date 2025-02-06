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

# Funkcja do sprawdzania, czy lokalizacja jest w Warszawie
def is_in_warsaw(lat, lon):
    # Granice Warszawy
    lat_min, lat_max = 52.0, 52.4
    lon_min, lon_max = 20.9, 21.3
    
    return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max

# Dodanie zgody na pobranie lokalizacji
st.title("Pobierz lokalizację użytkownika")
st.write("Aby uzyskać dokładną lokalizację, musisz wyrazić zgodę.")

if st.button("Pobierz lokalizację"):
    location = get_location()
    
    if location:
        lat, lon = location
        st.write(f"Twoja lokalizacja: Latitude = {lat}, Longitude = {lon}")
        
        # Sprawdzenie, czy lokalizacja jest w Warszawie
        if is_in_warsaw(lat, lon):
            st.write("Twoja lokalizacja znajduje się w Warszawie!")
            # Wyświetlanie mapy z lokalizacją
            st.map([{"lat": lat, "lon": lon}])
        else:
            st.warning("Twoja lokalizacja nie znajduje się w Warszawie.")
