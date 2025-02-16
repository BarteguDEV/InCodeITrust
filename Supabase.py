import streamlit as st
from supabase import create_client, Client

# Wczytanie danych z sekcji secrets
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["api_key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
bucket = supabase.storage.from_("Streamlit-BG-bucket")

def get_persons():
    """Pobiera unikalną listę osób z tabeli 'results'."""
    response = supabase.table("results").select("person").execute()
    if response.data:
        return sorted(list({row["person"] for row in response.data if row.get("person")}))
    return []

def get_venues():
    """Pobiera unikalną listę miejscówek z tabeli 'results'."""
    response = supabase.table("results").select("venue").execute()
    if response.data:
        return sorted(list({row["venue"] for row in response.data if row.get("venue")}))
    return []

def get_categories():
    """Pobiera unikalną listę kategorii z tabeli 'results'."""
    response = supabase.table("results").select("category").execute()
    if response.data:
        return sorted(list({row["category"] for row in response.data if row.get("category")}))
    return []

def initialize_records_if_needed(new_person=None, new_venue=None):
    """
    Dla nowo dodanej osoby lub miejscówki inicjuje rekordy we wszystkich kombinacjach.
    Jeśli dodajesz osobę, dla każdej istniejącej miejscówki i kategorii dodaj rekord.
    Jeśli dodajesz miejscówkę, dla każdej istniejącej osoby i kategorii dodaj rekord.
    """
    persons = get_persons()
    venues = get_venues()
    categories = get_categories()
    
    if new_person:
        # Inicjujemy rekordy dla nowej osoby we wszystkich miejscówkach i kategoriach
        for venue in venues:
            for cat in categories:
                response = supabase.table("results") \
                    .select("*") \
                    .eq("person", new_person) \
                    .eq("venue", venue) \
                    .eq("category", cat) \
                    .execute()
                if not response.data:
                    supabase.table("results").insert({
                        "person": new_person,
                        "venue": venue,
                        "category": cat,
                        "value": 0.0,
                        "initialized": True
                    }).execute()
                    st.write(f"Rekord {new_person} - {venue} - {cat} dodany do bazy.")
    
    if new_venue:
        # Inicjujemy rekordy dla nowej miejscówki dla każdej osoby i kategorii
        for person in persons:
            for cat in categories:
                response = supabase.table("results") \
                    .select("*") \
                    .eq("person", person) \
                    .eq("venue", new_venue) \
                    .eq("category", cat) \
                    .execute()
                if not response.data:
                    supabase.table("results").insert({
                        "person": person,
                        "venue": new_venue,
                        "category": cat,
                        "value": 0.0,
                        "initialized": True
                    }).execute()
                    st.write(f"Rekord {person} - {new_venue} - {cat} dodany do bazy.")

def upload_venue_image(selected_venue, bucket):
    if "uploaded" not in st.session_state:
        st.session_state["uploaded"] = False

    if not st.session_state["uploaded"]:  
        uploaded_file = st.file_uploader("Wybierz zdjęcie")

        if uploaded_file:
            file_name = f"{selected_venue}.jpg"  
            file_path = f"uploads/{file_name}"  

            try:
                # Usuń istniejący plik (jeśli istnieje)
                bucket.remove([file_path])

                # Prześlij nowy plik
                response = bucket.upload(file_path, uploaded_file.read())

                # Sprawdzamy, czy plik się wrzucił
                if hasattr(response, "full_path") or hasattr(response, "path"):
                    st.success("Zdjęcie zostało przesłane pomyślnie!")
                    st.session_state["uploaded"] = True  # Ustawienie flagi, aby ukryć file_uploader
                    st.rerun()  # Restart strony, ale tylko raz!
                else:
                    st.error(f"Błąd podczas przesyłania pliku: {response}")

            except Exception as e:
                st.error(f"Błąd podczas przesyłania pliku: {e}")
    else:
        st.info("Zdjęcie już zostało przesłane! Odśwież stronę, jeśli chcesz dodać nowe.")


# Tworzymy zakładki
t_users, t_venues, t_category = st.tabs(["Użytkownicy", "Miejscówki", "Kategorie"])

with t_users:
    st.subheader(":green-background[Dodaj użytkownika]")
    new_person = st.text_input("Nowy użytkownik", label_visibility="collapsed")
    if st.button("Dodaj użytkownika"):
        if new_person.strip() == "":
            st.error("Nazwa użytkownika nie może być pusta!")
        elif new_person in get_persons():
            st.info("Taki użytkownik już istnieje.")
        else:
            # Dodajemy nowego użytkownika poprzez inicjalizację odpowiednich rekordów
            initialize_records_if_needed(new_person=new_person)
            st.success(f"Dodano: {new_person}")
            st.rerun()  # Odświeżenie, aby pobrać aktualne dane

    st.divider()
    st.subheader(":red-background[Usuń użytkownika]")
    persons = get_persons()
    if persons:
        user_to_remove = st.selectbox("Wybierz użytkownika do usunięcia", persons, label_visibility="collapsed")
        if st.button("Usuń użytkownika"):
            # Przykładowo – usunięcie rekordu może oznaczać usunięcie wszystkich wpisów danej osoby
            delete_response = supabase.table("results").delete().eq("person", user_to_remove).execute()
            if delete_response.status_code == 200:
                st.success(f"Użytkownik '{user_to_remove}' został usunięty.")
                st.rerun()
            else:
                st.error("Nie udało się usunąć użytkownika.")
    else:
        st.info("Brak użytkowników w bazie.")

with t_venues:
    st.subheader(":green-background[Dodaj miejscówkę]")
    new_venue = st.text_input("Nowa miejscówka", label_visibility="collapsed")
    if st.button("Dodaj miejscówkę"):
        if new_venue.strip() == "":
            st.error("Nazwa miejscówki nie może być pusta!")
        elif new_venue in get_venues():
            st.info("Taka miejscówka już istnieje.")
        else:
            initialize_records_if_needed(new_venue=new_venue)
            st.success(f"Miejscówka '{new_venue}' została dodana.")
            st.rerun()
    
    st.divider()
    st.subheader(":red-background[Usuń miejscówkę]")
    venues = get_venues()
    if venues:
        venue_to_remove = st.selectbox("Wybierz miejscówkę do usunięcia", venues, label_visibility="collapsed")
        if st.button("Usuń miejscówkę"):
            delete_response = supabase.table("results").delete().eq("venue", venue_to_remove).execute()
            if delete_response.status_code == 200:
                st.success(f"Miejscówka '{venue_to_remove}' została usunięta.")
                st.rerun()
            else:
                st.error("Nie udało się usunąć miejscówki.")
    else:
        st.info("Brak miejscówek w bazie.")

    st.divider()
    st.subheader(":orange-background[Dodaj zdjęcie]")
    venues = get_venues()
    if venues:
        selected_venue = st.selectbox("Wybierz miejscówkę", venues, label_visibility="collapsed")
        
        # Wywołanie funkcji do uploadu zdjęcia
        upload_venue_image(selected_venue, bucket)
        
    else:
        st.info("Brak dostępnych miejscówek w bazie.")


with t_category:
    st.subheader(":green-background[Results]")
    # Wyświetlamy podsumowanie tabeli 'results'
    response = supabase.table("results").select("*").execute()
    if response.data:
        st.json(response.data)
    else:
        st.info("Brak rekordów w bazie.")

    st.subheader(":green-background[Comments]")
    # Wyświetlamy podsumowanie tabeli 'results'
    response = supabase.table("comments").select("*").execute()
    if response.data:
        st.json(response.data)
    else:
        st.info("Brak rekordów w bazie.")
