import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from supabase import create_client, Client
from datetime import datetime, timedelta

# Wczytaj dane z sekcji secrets
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["api_key"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
bucket = supabase.storage.from_("Streamlit-BG-bucket")


# Funkcje pomocnicze do pobierania danych z bazy
def get_persons():
    response = supabase.table("results").select("person").execute()
    if response.data:
        return sorted(list({row["person"] for row in response.data if row.get("person")}))
    return []

def get_venues():
    response = supabase.table("results").select("venue").execute()
    if response.data:
        return sorted(list({row["venue"] for row in response.data if row.get("venue")}))
    return []

def get_categories():
    response = supabase.table("results").select("category").execute()
    if response.data:
        return sorted(list({row["category"] for row in response.data if row.get("category")}))
    return []

# Inicjalne pobranie list z bazy
persons = get_persons()
venues = get_venues()
categories = get_categories()

st.title(":green[Wyjścia Melanże]")
st.caption('Projekt: "Kim Pan Był" v.5  Współfinansowany przez własną kieszeń. Proszę uzupełniać na bieżąco || Skala ocen od 0-7,5')

tab1, tab2 = st.tabs(["Ankieta", "Wykresiki"])

def display_venue_image(selected_venue, bucket, venues: list):
    """
    Sprawdza, czy dla wybranej miejscówki istnieje plik w bucketcie. 
    Jeśli tak – pobiera publiczny URL i wyświetla zdjęcie, 
    w przeciwnym razie informuje, że zdjęcie nie istnieje.
    """
    if selected_venue:
        file_name = f"{selected_venue}.jpg"
        file_path = f"uploads/{file_name}"
        files = bucket.list("uploads")
        file_exists = any(file.get("name") == file_name for file in files)
        if file_exists:
            image_url = bucket.get_public_url(file_path)
            st.image(image_url, width=500)
        else:
            st.info(f"Brak zdjęcia dla miejscówki - {selected_venue}")

@st.dialog("Edytuj odpowiedzi", width="small")
def edit_answers():
    global persons, venues
    # Upewnij się, że w session_state mamy wybraną osobę i miejscówkę
    if "selected_person" not in st.session_state or st.session_state.selected_person is None:
        st.session_state.selected_person = persons[0] if persons else None
    if "selected_venue" not in st.session_state or st.session_state.selected_venue is None:
        st.session_state.selected_venue = venues[0] if venues else None

    selected_person = st.session_state.selected_person
    selected_venue = st.session_state.selected_venue

    if selected_person is None or selected_venue is None:
        st.error("Nie wybrano osoby lub miejsca. Proszę wybrać je przed edytowaniem.")
        return

    if selected_person not in st.session_state.results or selected_venue not in st.session_state.results[selected_person]:
        st.error("Brak danych dla wybranej osoby i miejsca.")
        return

    current_answers = st.session_state.results[selected_person][selected_venue]
    
    # Ustalona kolejność kategorii (wszystkie porównujemy w uppercase)
    ordered_categories = ["DRINK", "FOOD", "WYSTRÓJ", "OBSŁUGA", "PERFORMANCE PER PRICE", "INNE"]
    # Filtrowanie – pomijamy ewentualne specjalne wpisy, np. "ŚREDNIA Z PUNKTÓW", "ŚREDNIA Z MIEJSCÓWKI"
    sorted_answers = sorted(
        [entry for entry in current_answers if entry["KATEGORIA"] not in ["ŚREDNIA Z PUNKTÓW", "ŚREDNIA Z MIEJSCÓWKI"]],
        key=lambda entry: ordered_categories.index(entry["KATEGORIA"].upper()) 
            if entry["KATEGORIA"].upper() in ordered_categories 
            else float('inf')
    )
    
    new_answers = {}
    with st.form(key="survey_edit_form"):
        for entry in sorted_answers:
            cat = entry["KATEGORIA"]
            default_val = float(entry["WARTOŚĆ"]) if isinstance(entry["WARTOŚĆ"], (int, float)) else 0.0
            new_value = st.slider(
                f":green-background[{cat}]",
                min_value=0.0,
                max_value=7.5,
                value=default_val,
                step=0.5,
                format="%.1f",
                label_visibility="visible",
                key=f"slider_{cat}"
            )
            new_answers[cat] = new_value

        submitted = st.form_submit_button("Zapisz zmiany")
        if submitted:
            try:
                # Aktualizacja wyników w session_state
                st.session_state.results[selected_person][selected_venue] = [
                    {"KATEGORIA": cat, "WARTOŚĆ": new_answers[cat]} for cat in new_answers
                ]
                # Zapis do bazy Supabase
                for cat, val in new_answers.items():
                    response = supabase.table("results").select("*") \
                        .eq("person", selected_person) \
                        .eq("venue", selected_venue) \
                        .eq("category", cat).execute()
                    if response.data:
                        supabase.table("results").update({
                            "value": val,
                            "initialized": True
                        }).eq("person", selected_person).eq("venue", selected_venue).eq("category", cat).execute()
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Wystąpił błąd: {e}")


@st.dialog("Dodaj komentarz", width="small")
def add_comment_dialog():
    global venues
    if "selected_venue" not in st.session_state or st.session_state.selected_venue is None:
        st.session_state.selected_venue = venues[0] if venues else None
    if "comments" not in st.session_state:
        st.session_state.comments = {venue: [] for venue in venues}
    
    with st.form(key="comment_form"):
        new_comment = st.text_area("Wpisz swój komentarz", key="new_comment")
        submitted = st.form_submit_button("Zapisz komentarz")
        if submitted:
            if new_comment.strip():
                st.session_state.comments[st.session_state.selected_venue].append(new_comment)
                supabase.table("comments").insert({
                    "venue": st.session_state.selected_venue,
                    "comment": new_comment
                }).execute()
                st.success("Komentarz dodany pomyślnie.")
                st.experimental_rerun()
            else:
                st.warning("Komentarz nie może być pusty!")

with tab1:
    # Pobierz aktualne dane z bazy
    persons = get_persons()
    venues = get_venues()
    categories = get_categories()

    selected_person = st.selectbox(":green-background[Wybierz osobę]", persons)
    selected_venue = st.selectbox(":green-background[Wybierz miejscówkę]", venues)

    # Zapisz wybrane wartości do session_state
    st.session_state.selected_person = selected_person
    st.session_state.selected_venue = selected_venue

    # Inicjalizacja stanu aplikacji – jeżeli jeszcze nie istnieje, utwórz słownik 'results'
    if "results" not in st.session_state:
        st.session_state.results = {}

    for person in persons:
        if person not in st.session_state.results:
            st.session_state.results[person] = {}
        for venue in venues:
            if venue not in st.session_state.results[person]:
                # Pobierz dane z bazy dla danej pary osoba-miejscówka
                response = supabase.table("results").select("category, value") \
                    .eq("person", person).eq("venue", venue).execute()
                if response.data:
                    st.session_state.results[person][venue] = [
                        {"KATEGORIA": entry["category"], "WARTOŚĆ": entry["value"]} for entry in response.data
                    ]
                else:
                    st.session_state.results[person][venue] = [
                        {"KATEGORIA": cat, "WARTOŚĆ": 0.0} for cat in categories
                    ]

    current_answers = st.session_state.results[selected_person][selected_venue]

    display_venue_image(selected_venue, bucket, venues)

    c1, c2, c3 = st.columns([0.5, 1.1, 0.1])
    with c1:
        if st.button(":blue[Edytuj odpowiedzi]"):
            edit_answers()
    with c2:
        if st.button(":blue[Dodaj komentarz]"):
            add_comment_dialog()

    # Budowanie finalnego DataFrame tylko dla wybranej pary
    rows = []
    for entry in current_answers:
        rows.append({
            "KATEGORIA": entry["KATEGORIA"],
            "WARTOŚĆ": entry["WARTOŚĆ"]
        })
    ordered_categories = ["DRINK", "FOOD", "WYSTRÓJ", "OBSŁUGA", "PERFORMANCE PER PRICE", "INNE"]
    rows = sorted(rows, key=lambda x: ordered_categories.index(x["KATEGORIA"]) if x["KATEGORIA"] in ordered_categories else float('inf'))

    if rows:
        df = pd.DataFrame(rows)
        st.data_editor(
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

def fetch_comments(venue):
    response = supabase.table("comments").select("id, comment, created_at") \
        .eq("venue", venue).order("created_at", desc=True).execute()
    return response.data if response.data else []

def format_datetime(timestamp):
    try:
        dt_obj = datetime.strptime(timestamp[:19], "%Y-%m-%dT%H:%M:%S")
        dt_obj = dt_obj + timedelta(hours=1)
        return dt_obj.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return "Nieznana data"

def display_comments(venue):
    st.subheader(f"💬 Komentarze dla {venue}")
    comments = fetch_comments(venue)
    if comments:
        for comment in comments:
            with st.container():
                st.write(f"🗨️ {comment['comment']}")
                formatted_date = format_datetime(comment["created_at"])
                st.caption(f"📅 {formatted_date}")
    else:
        st.info("Brak komentarzy dla tej miejscówki. Bądź pierwszym, który doda komentarz! 🎉")

display_comments(selected_venue)
