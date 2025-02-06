import streamlit as st
import os
import json
from supabase import create_client, Client
import supabase

CONFIG_FILE = "config.json"
# Wczytaj dane z sekcji secrets
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["api_key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def load_config():
    """Wczytuje konfigurację z pliku JSON."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {
            "persons": [],
            "venues": [],
            "categories": []
        }

def save_config(config):
    """Zapisuje konfigurację do pliku JSON."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def add_user(list_name, item):
    """
    Dodaje element do wybranej listy w konfiguracji.
    list_name: "persons", "venues" lub "categories"
    item: element do dodania
    """
    config = load_config()
    if item not in config.get(list_name, []):
        config[list_name].append(item)
        save_config(config)


def remove_user(user):
    """
    Usuwa użytkownika (element z listy "persons") z konfiguracji.
    """
    config = load_config()
    if user in config.get("persons", []):
        config["persons"].remove(user)
        save_config(config)
        return True
    return False

def update_user(old_user, new_user):
    """
    Modyfikuje istniejącego użytkownika.
    Zamienia wartość old_user na new_user w liście "persons".
    """
    config = load_config()
    persons = config.get("persons", [])
    if old_user in persons:
        index = persons.index(old_user)
        persons[index] = new_user
        save_config(config)
        return True
    return False

def add_venue(venue):
    """
    Dodaje nową miejscówkę do listy 'venues' w konfiguracji.
    Jeśli miejscówka już istnieje, nie zostanie dodana.
    """
    config = load_config()
    if venue not in config.get("venues", []):
        config["venues"].append(venue)
        save_config(config)
        return True
    return False

def remove_venue(venue):
    """
    Usuwa miejscówkę z listy 'venues' w konfiguracji.
    """
    config = load_config()
    if venue in config.get("venues", []):
        config["venues"].remove(venue)
        save_config(config)
        return True
    return False

def initialize_records_if_needed():
    persons = config["persons"]
    venues = config["venues"]
    categories = config["categories"]
    for person in persons:
        for venue in venues:
            for cat in categories:
                # Sprawdzamy, czy rekord z tymi danymi już istnieje i czy jest zainicjowany
                response = supabase.table("results").select("*").eq("person", person).eq("venue", venue).eq("category", cat).execute()
                if not response.data or response.data[0]["initialized"] == False:
                    # Rekord nie istnieje lub nie jest zainicjowany, więc dodajemy go
                    supabase.table("results").insert({
                        "person": person,
                        "venue": venue,
                        "category": cat,
                        "value": 0.0,  # Domyślna wartość
                        "initialized": True  # Oznaczamy rekord jako zainicjowany
                    }).execute()
                    print(f"Rekord {person} - {venue} - {cat} został dodany do bazy!")


# Wczytanie aktualnej konfiguracji
config = load_config()

t_users, t_venues, t_category = st.tabs(["Użytkownicy", "Miejscówki", "Kategorie"])
# Wczytanie aktualnej konfiguracji
config = load_config()
persons = config.get("persons", [])
venues = config.get("venues", [])
categories = config.get("categories", [])

with t_users:
    # Dodawanie nowego użytkownika
    st.subheader(":green-background[Dodaj użytkownika]")
    new_person = st.text_input(":green-background[Nowy użytkownik]")
    if st.button("Dodaj użytkownika"):
        add_user("persons", new_person)
        initialize_records_if_needed()
        st.success(f"Dodano: {new_person}")
        st.rerun()  # Przeładowanie aplikacji, aby wczytać nowe dane

    # Usuwanie użytkownika
    st.subheader(":red-background[Usuń użytkownika]")
    user_to_remove = st.selectbox(":red-background[Wybierz użytkownika do usunięcia]", persons)
    if st.button("Usuń użytkownika"):
        if remove_user(user_to_remove):
            st.success(f"Użytkownik '{user_to_remove}' został usunięty.")
            st.rerun()  # Odświeżenie, aby wczytać zmienioną konfigurację
        else:
            st.error("Nie udało się usunąć użytkownika.")

    # Modyfikacja użytkownika
    st.subheader(":orange-background[Modyfikuj użytkownika]")
    old_user = st.selectbox(":orange-background[Wybierz użytkownika do modyfikacji]", persons, key="old_user")
    new_user = st.text_input(":orange-background[Podaj nową nazwę użytkownika]", key="new_user")
    if st.button("Zaktualizuj użytkownika"):
        if new_user.strip() == "":
            st.error("Nowa nazwa nie może być pusta!")
        elif config.update_user(old_user, new_user):
            st.success(f"Użytkownik '{old_user}' został zmieniony na '{new_user}'.")
            st.rerun()
        else:
            st.error("Nie udało się zaktualizować użytkownika.")

with t_venues:
    # Dodawanie nowej miejscówki
    st.subheader(":green-background[Dodaj miejscówkę]")
    new_venue = st.text_input(":green-background[Nowa miejscówka]")
    if st.button("Dodaj miejscówkę"):
        if new_venue.strip() == "":
            st.error("Nazwa miejscówki nie może być pusta!")
        elif add_venue(new_venue):
            initialize_records_if_needed()
            st.success(f"Miejscówka '{new_venue}' została dodana.")
            st.rerun()  # Przeładuj aplikację, aby wczytać zaktualizowaną konfigurację
        else:
            st.info("Taka miejscówka już istnieje.")

    # Usuwanie miejscówki
    st.subheader(":red-background[Usuń miejscówkę]")
    venue_to_remove = st.selectbox(":red-background[Wybierz miejscówkę do usunięcia]", venues)
    if st.button("Usuń miejscówkę"):
        if remove_venue(venue_to_remove):
            st.success(f"Miejscówka '{venue_to_remove}' została usunięta.")
            st.rerun()
        else:
            st.error("Nie udało się usunąć miejscówki.")

with t_venues:
    # Lista dostępnych miejscówek
    venues_img = ["SKUNSTREFA", "PIZZA", "KFC"]

    # Inicjalizacja słownika w session_state
    if "venue_images" not in st.session_state:
        st.session_state.venue_images = {venue: "" for venue in venues_img}

    # Sekcja do wrzucania zdjęć
    st.subheader("Dodaj zdjęcie do miejscówki")
    selected_venue = st.selectbox("Wybierz miejscówkę", venues)
    uploaded_file = st.file_uploader("Prześlij zdjęcie", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None and selected_venue:
        bucket = supabase.storage.from_('Streamlit-BG-bucket')
        file_bytes = uploaded_file.read()
        
        # Ścieżka w bucketcie z unikalną nazwą dla danej miejscówki
        file_path = f"uploads/{selected_venue}.jpg"
        
        # Wgrywanie zdjęcia do bucketu (możesz dodać opcję upsert, np. file_options={"upsert": "true"})
        bucket.upload(file_path, file_bytes)
        
        # Pobranie publicznego URL
        public_url = bucket.get_public_url(file_path)
        
        # Aktualizacja słownika w session_state
        st.session_state.venue_images[selected_venue] = public_url
        
        st.success(f"Zdjęcie dla {selected_venue} przesłane do chmury!")