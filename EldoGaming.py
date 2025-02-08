import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from supabase import create_client, Client
import json
from datetime import datetime, timedelta


# Wczytaj dane konfiguracyjne
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)


# Wczytaj dane z sekcji secrets
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["api_key"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
bucket = supabase.storage.from_('Streamlit-BG-bucket')


st.title(":green[Wyjścia Melanże]")
st.caption('Projekt: "Kim Pan Był" v.5  Współfinansowany przez własną kieszeń. Proszę uzupełniać na bieżąco || Skala ocen od 0-7,5')

tab1, tab2 = st.tabs(["Ankieta", "Wykresiki"])

def display_venue_image(selected_venue, bucket, venues: list):
    """
    Funkcja sprawdza, czy dla wybranej miejscówki istnieje plik w bucketcie. 
    Jeśli tak – pobiera publiczny URL i wyświetla zdjęcie, 
    w przeciwnym razie informuje, że zdjęcie nie istnieje.
    
    :param selected_venue: Nazwa miejscówki (np. "SKUNSTREFA")
    :param bucket: Obiekt bucket z Supabase (np. supabase.storage.from_('nazwa-bucketu'))
    :param venues: Lista dostępnych miejscówek (używana np. przy selectboxie)
    """
    if selected_venue:
        # Nazwa pliku i ścieżka – zakładamy, że zdjęcie zapisujemy jako "{selected_venue}.jpg"
        file_name = f"{selected_venue}.jpg"
        file_path = f"uploads/{file_name}"
        
        # Pobieramy listę plików znajdujących się w folderze "uploads"
        files = bucket.list("uploads")
        # Zakładamy, że pliki zwracane są jako lista słowników, gdzie klucz "name" zawiera nazwę pliku.
        file_exists = any(file.get("name") == file_name for file in files)
        
        if file_exists:
            image_url = bucket.get_public_url(file_path)
            st.image(image_url, width=500)
        else:
            st.info("Brak zdjęcia dla wybranej miejscówki.")

# Funkcja dialogowa do edycji odpowiedzi
@st.dialog("Edytuj odpowiedzi", width="small")
def edit_answers():
    # Inicjalizuj wartości w session_state, jeśli nie istnieją
    if "selected_person" not in st.session_state or st.session_state.selected_person is None:
        st.session_state.selected_person = persons[0]  # Domyślnie pierwsza osoba

    if "selected_venue" not in st.session_state or st.session_state.selected_venue is None:
        st.session_state.selected_venue = venues[0]  # Domyślnie pierwsza miejscówka

    # Aktualizacja stanu w session_state tylko wtedy, gdy wartości zostały zmienione
    if selected_person != st.session_state.selected_person:
        st.session_state.selected_person = selected_person

    if selected_venue != st.session_state.selected_venue:
        st.session_state.selected_venue = selected_venue

    # Sprawdzanie, czy wybrana osoba i miejsce są poprawnie przypisane
    if selected_person is None or selected_venue is None:
        st.error("Nie wybrano osoby lub miejsca. Proszę wybrać je przed edytowaniem.")
        return  # Kończy działanie funkcji, jeśli nie ma wybranej osoby lub miejsca

    # Sprawdzenie, czy istnieją dane dla wybranej osoby i miejsca
    if selected_person not in st.session_state.results or selected_venue not in st.session_state.results[selected_person]:
        st.error("Brak danych dla wybranej osoby i miejsca.")
        return  # Kończy działanie funkcji, jeśli brak danych

    current_answers = st.session_state.results[selected_person][selected_venue]
    
    new_answers = {}
    with st.form(key="survey_edit_form"):
        for entry in current_answers:
            cat = entry["KATEGORIA"]
            if cat not in ["ŚREDNIA Z PUNKTÓW", "ŚREDNIA Z MIEJSCÓWKI"]:
                # Ustalamy domyślną wartość slajdera
                default_val = float(entry["WARTOŚĆ"]) if isinstance(entry["WARTOŚĆ"], (int, float)) else 0.0
                new_value = st.slider(
                    f":green-background[{cat}]",
                    min_value=0.0,
                    max_value=7.5,
                    value=default_val,
                    step=0.5,
                    format="%.1f",
                    label_visibility="visible",
                    key=f"slider_{cat}"  # Unikalny klucz dla każdego slidera
                )
                new_answers[cat] = new_value


        submitted = st.form_submit_button("Zapisz zmiany")
        if submitted:
            try:
                # Aktualizacja wyników w session_state
                st.session_state.results[selected_person][selected_venue] = [
                    {"KATEGORIA": cat, "WARTOŚĆ": new_answers[cat]} for cat in new_answers
                ]

                # Zapis do Supabase
                for cat, val in new_answers.items():
                    # Sprawdzamy, czy rekord istnieje w bazie
                    response = supabase.table("results").select("*").eq("person", selected_person).eq("venue", selected_venue).eq("category", cat).execute()

                    if response.data:
                        # Rekord istnieje, więc wykonujemy aktualizację
                        update_response = supabase.table("results").update({
                            "value": val,
                            "initialized": True  # Możemy również ustawić flagę, jeśli chcesz
                        }).eq("person", selected_person).eq("venue", selected_venue).eq("category", cat).execute()
                st.rerun()  # Odświeżenie strony po zapisaniu
            except Exception as e:
                st.error(f"Wystąpił błąd: {e}")

# Funkcja dialogowa do dodawania komentarza
@st.dialog("Dodaj komentarz", width="small")
def add_comment_dialog():
    # Upewnij się, że wybrana miejscówka jest ustawiona; domyślnie pierwsza z listy
    if "selected_venue" not in st.session_state or st.session_state.selected_venue is None:
        st.session_state.selected_venue = venues[0]
    # Inicjalizacja struktury komentarzy w session_state, jeśli jeszcze nie istnieje
    if "comments" not in st.session_state:
        st.session_state.comments = {venue: [] for venue in venues}
    
    with st.form(key="comment_form"):
        new_comment = st.text_area("Wpisz swój komentarz", key="new_comment")
        submitted = st.form_submit_button("Zapisz komentarz")
        if submitted:
            if new_comment.strip():
                # Dodaj komentarz do lokalnej struktury (session_state)
                st.session_state.comments[st.session_state.selected_venue].append(new_comment)
                
                # Wstaw komentarz do bazy Supabase
                response = supabase.table("comments").insert({
                    "venue": st.session_state.selected_venue,
                    "comment": new_comment
                }).execute()
                st.success("Komentarz dodany pomyślnie.")
                
                st.rerun()  # Odświeżenie strony po zapisaniu
            else:
                st.warning("Komentarz nie może być pusty!")



with tab1:
    # Lista opcji
    persons = config.get("persons", [])
    venues = config.get("venues", [])
    categories = config.get("categories", [])

    selected_person = st.selectbox(":green-background[Wybierz osobę]", persons)
    selected_venue = st.selectbox(":green-background[Wybierz miejscówkę]", venues)


    # Inicjalizacja stanu aplikacji – jeśli już istnieje, nie nadpisujemy go
    if "results" not in st.session_state:
        st.session_state.results = {}

    for person in persons:
        if person not in st.session_state.results:
            st.session_state.results[person] = {}

        for venue in venues:
            if venue not in st.session_state.results[person]:
                # Pobranie danych z Supabase
                response = supabase.table("results").select("category, value").eq("person", person).eq("venue", venue).execute()

                if response.data:
                    st.session_state.results[person][venue] = [
                        {"KATEGORIA": entry["category"], "WARTOŚĆ": entry["value"]} for entry in response.data
                    ]
                else:
                    st.session_state.results[person][venue] = [{"KATEGORIA": cat, "WARTOŚĆ": 0.0} for cat in categories]

    current_answers = st.session_state.results[selected_person][selected_venue]

    display_venue_image(selected_venue,bucket, venues)

    c1,c2,c3 = st.columns([1,1,1])
    with c1:
        if st.button(":blue[Edytuj odpowiedzi]"):
            edit_answers()

    with c1:
        if st.button(":blue[Dodaj komentarz]"):
            add_comment_dialog()

    # Budowanie finalnego DataFrame tylko dla wybranej pary
    rows = []
    for entry in current_answers:
        rows.append({
            "KATEGORIA": entry["KATEGORIA"],
            "WARTOŚĆ": entry["WARTOŚĆ"]
        })
    ordered_categories = [
        "FOOD", 
        "WYSTRÓJ", 
        "OBSŁUGA", 
        "PERFORMANCE PER PRICE", 
        "INNE"
    ]
    rows = sorted(rows, key=lambda x: ordered_categories.index(x["KATEGORIA"]) if x["KATEGORIA"] in ordered_categories else float('inf'))

    if rows:
        df = pd.DataFrame(rows)
        dfa = st.data_editor(
            df,
            column_config={
                "WARTOŚĆ": st.column_config.ProgressColumn(
                    "Wartość", 
                    help="Wartość wyrażona jako progress bar",
                    format="%.1f",
                    min_value=0,
                    max_value=7.5,
                ),
            },
            hide_index=True,
            disabled=["KATEGORIA"],
        )

st.divider()
# Funkcja do pobierania komentarzy z Supabase
def fetch_comments(venue):
    response = supabase.table("comments").select("id, comment, created_at").eq("venue", venue).order("created_at", desc=True).execute()
    return response.data if response.data else []

# Funkcja do formatowania daty
def format_datetime(timestamp):
    try:
        dt_obj = datetime.strptime(timestamp[:19], "%Y-%m-%dT%H:%M:%S")  # Konwersja ISO na datetime
        dt_obj = dt_obj + timedelta(hours=1)  # Dodanie 1 godziny
        return dt_obj.strftime("%Y-%m-%d %H:%M:%S")  # Formatowanie daty
    except ValueError:
        return "Nieznana data"

# Pobranie i wyświetlenie komentarzy
def display_comments(venue):
    st.subheader(f"💬 Komentarze dla {venue}")
    comments = fetch_comments(venue)

    if comments:
        for comment in comments:
            with st.container():
                st.write(f"🗨️ {comment['comment']}")
                formatted_date = format_datetime(comment['created_at'])
                st.caption(f"📅 {formatted_date}")
    else:
        st.info("Brak komentarzy dla tej miejscówki. Bądź pierwszym, który doda komentarz! 🎉")

# Wywołanie funkcji wyświetlającej komentarze
display_comments(selected_venue)