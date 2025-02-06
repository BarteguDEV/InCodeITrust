import streamlit as st
import time

# HTML i JavaScript do pobrania lokalizacji użytkownika
html_code = """
<script>
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                let coords = position.coords.latitude + "," + position.coords.longitude;
                let queryParams = new URLSearchParams(window.location.search);
                queryParams.set("location", coords);
                window.location.search = queryParams.toString();
            },
            function(error) {
                console.log("Błąd pobierania lokalizacji: " + error.message);
            }
        );
    } else {
        console.log("Geolokalizacja nie jest wspierana przez przeglądarkę.");
    }
}
</script>
<button onclick="getLocation()">📍 Pobierz moją lokalizację</button>
"""

st.components.v1.html(html_code)

# Pobranie współrzędnych z query params
query_params = st.query_params
location = query_params.get("location")

if location:
    lat, lon = map(float, location.split(","))
    
    # Sprawdzenie, czy lokalizacja jest w Warszawie
    if 52.0 <= lat <= 52.4 and 20.8 <= lon <= 21.3:
        st.success(f"Twoja lokalizacja: Latitude = {lat}, Longitude = {lon} (Warszawa)")
    else:
        st.warning(f"Twoja lokalizacja: Latitude = {lat}, Longitude = {lon} (Poza Warszawą)")

    # Wyświetlenie mapy
    st.map([{"lat": lat, "lon": lon}])
else:
    st.info("Kliknij przycisk, aby pobrać swoją lokalizację.")
