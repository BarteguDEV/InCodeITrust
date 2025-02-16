import streamlit as st
import pandas as pd
import time
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
@st.cache_data(ttl=300)
def get_persons():
    response = supabase.table("results").select("person").execute()
    if response.data:
        return sorted(list({row["person"] for row in response.data if row.get("person")}))
    return []

@st.cache_data(ttl=300)
def get_venues():
    response = supabase.table("results").select("venue").execute()
    if response.data:
        return sorted(list({row["venue"] for row in response.data if row.get("venue")}))
    return []

@st.cache_data(ttl=300)
def get_categories():
    response = supabase.table("results").select("category").execute()
    if response.data:
        return sorted(list({row["category"] for row in response.data if row.get("category")}))
    return []

@st.cache_data(ttl=300)
def get_all_results():
    """
    Pobiera wszystkie rekordy z tabeli `results` jednym zapytaniem.
    """
    response = supabase.table("results").select("person, venue, category, value").execute()
    return response.data if response.data else []

@st.cache_data(ttl=300)
def fetch_comments(venue):
    response = supabase.table("comments").select("id, comment, created_at, person") \
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
                formatted_date = format_datetime(comment["created_at"])
                user = comment.get("person", "Nieznany użytkownik")
                st.caption(f"🤷 {user} ┃ 🗨️ {comment['comment']} ┃ 📅 {formatted_date}")
    else:
        st.info("Brak komentarzy dla tej miejscówki. Bądź pierwszym, który doda komentarz! 🎉")

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
            st.info("Brak zdjęcia dla miejscówki")

@st.dialog("Edytuj odpowiedzi", width="small")
def edit_answers():
    global persons, venues

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
    
    ordered_categories = ["DRINK", "FOOD", "WYSTRÓJ", "OBSŁUGA", "PERFORMANCE PER PRICE", "INNE"]
    
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
                # Aktualizacja wartości w session_state
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
                
                # Wyczyść cache, aby pobrać nowe wartości
                get_all_results.clear()

                # Zwiększenie licznika aktualizacji (przeładowuje tylko dataframe)
                if "results_update" not in st.session_state:
                    st.session_state.results_update = 0
                st.session_state.results_update += 1

                # Zamknięcie okna dialogowego i wymuszenie odświeżenia
                st.session_state.show_dialog = False
                st.rerun()

            except Exception as e:
                st.error(f"Wystąpił błąd: {e}")


@st.dialog("Dodaj komentarz", width="small")
def add_comment_dialog():
    global venues, persons  # Upewnij się, że zmienna persons jest dostępna globalnie
    if "selected_venue" not in st.session_state or st.session_state.selected_venue is None:
        st.session_state.selected_venue = venues[0] if venues else None
    if "comments" not in st.session_state:
        st.session_state.comments = {venue: [] for venue in venues}
    
    with st.form(key="comment_form"):
        new_comment = st.text_area("Wpisz swój komentarz", key="new_comment")
        comment_user = st.selectbox("Wybierz użytkownika", persons, key="comment_user")
        audio_value = st.audio_input("Record a voice message")
        submitted = st.form_submit_button("Zapisz komentarz")
        if submitted:
            if new_comment.strip():
                st.session_state.comments[st.session_state.selected_venue].append(new_comment)
                supabase.table("comments").insert({
                    "venue": st.session_state.selected_venue,
                    "comment": new_comment,
                    "person": comment_user  # Zapisanie wybranego użytkownika do kolumny 'person'
                }).execute()
                st.success("Komentarz dodany pomyślnie.")
                time.sleep(1)
                st.rerun()
            else:
                st.warning("Komentarz nie może być pusty!")

# Inicjalne pobranie list z bazy
persons = get_persons()
venues = get_venues()
categories = get_categories()

st.title(":green[Zbiór miejscówek i ocen]")
st.caption('Projekt: "Kim Pan Był" v.5  Współfinansowany przez własną kieszeń. Proszę uzupełniać na bieżąco || Skala ocen od 0-7.5')

tab1, tab2 = st.tabs(["Ankieta", "Wykresiki"])

with tab1:
    # Pobierz aktualne dane z bazy
    persons = get_persons()
    venues = get_venues()
    categories = get_categories()

    selected_person = st.segmented_control(
        "person picker",
        persons,
        selection_mode="single",
        key="persons_pills",
        default=persons[0] if persons else '1',
        label_visibility="collapsed"
    )
    selected_venue = st.selectbox(":green-background[Wybierz miejscówkę]", venues)

    # Zapisz wybrane wartości do session_state
    st.session_state.selected_person = selected_person
    st.session_state.selected_venue = selected_venue

    # Inicjalizacja stanu aplikacji – jeżeli jeszcze nie istnieje, utwórz słownik 'results'
    if "results" not in st.session_state:
        st.session_state.results = {}

    # Pobierz wszystkie wyniki za jednym zapytaniem
    all_results = get_all_results()

    for person in persons:
        if person not in st.session_state.results:
            st.session_state.results[person] = {}
        for venue in venues:
            # Filtrowanie wyników dla danej pary osoba-miejscówka
            results_for_pair = [
                {"KATEGORIA": entry["category"], "WARTOŚĆ": entry["value"]}
                for entry in all_results 
                if entry["person"] == person and entry["venue"] == venue
            ]
            if results_for_pair:
                st.session_state.results[person][venue] = results_for_pair
            else:
                st.session_state.results[person][venue] = [
                    {"KATEGORIA": cat, "WARTOŚĆ": 0.0} for cat in categories
                ]

    current_answers = st.session_state.results[selected_person][selected_venue]

    display_venue_image(selected_venue, bucket, venues)

    if "show_dialog" not in st.session_state:
        st.session_state.show_dialog = False  # Domyślnie dialog zamknięty

    if st.button(":blue[Edytuj odpowiedzi]"):
        st.session_state.show_dialog = True  # Otwórz dialog

    # Pokazujemy okno dialogowe tylko jeśli flaga `show_dialog` jest True
    if st.session_state.show_dialog:
        edit_answers()

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
            key=f"data_editor_{st.session_state.get('results_update', 0)}",
            column_config={
                "KATEGORIA": st.column_config.TextColumn("KATEGORIA", width=170),
                "WARTOŚĆ": st.column_config.ProgressColumn(
                    "Wartość", 
                    format="%.1f",
                    min_value=0,
                    max_value=7.5,
                ),
            },
            hide_index=True,
            disabled=["KATEGORIA"],
        )
    st.divider()

with tab1:
    if st.button(":blue[Dodaj komentarz]"):
        add_comment_dialog()
    display_comments(selected_venue)

with tab2:
    # Pobieramy dane za pomocą funkcji get_all_results() i konwertujemy je do DataFrame
    data = get_all_results()
    df = pd.DataFrame(data)

    st.title("Raporty wyników")

    # Tworzymy zakładki dla raportów
    tabs = st.tabs(["Ogólny", "Osoby", "Miejscówki", "Interaktywny"])

    with tabs[0]:
        st.header("Raport Ogólny: Średnia wartość per kategoria")
        # Obliczamy średnią wartość dla każdej kategorii
        category_avg = df.groupby("category")["value"].mean().reset_index()
        st.dataframe(category_avg)
        
        # Wykres słupkowy
        fig, ax = plt.subplots()
        sns.barplot(data=category_avg, x="category", y="value", ax=ax)
        ax.set_title("Średnia wartość per kategoria")
        ax.set_xlabel("Kategoria")
        ax.set_ylabel("Średnia wartość")
        st.pyplot(fig)

    with tabs[1]:
        st.header("Raport: Średnia wartość per osoba i kategoria")
        # Tworzymy tabelę przestawną: osoby jako wiersze, kategorie jako kolumny
        pivot_person = df.pivot_table(index="person", columns="category", values="value", aggfunc="mean")
        st.dataframe(pivot_person)
        
        # Heatmapa dla wyników per osoba
        fig, ax = plt.subplots(figsize=(10,6))
        sns.heatmap(pivot_person, annot=True, fmt=".1f", cmap="viridis", ax=ax)
        ax.set_title("Heatmap: Średnia wartość per osoba i kategoria")
        st.pyplot(fig)

    with tabs[2]:
        st.header("Raport: Średnia wartość per miejscówka i kategoria")
        # Tworzymy tabelę przestawną: miejscówki jako wiersze, kategorie jako kolumny
        pivot_venue = df.pivot_table(index="venue", columns="category", values="value", aggfunc="mean")
        st.dataframe(pivot_venue)
        
        # Heatmapa dla wyników per miejscówka
        fig, ax = plt.subplots(figsize=(10,6))
        sns.heatmap(pivot_venue, annot=True, fmt=".1f", cmap="magma", ax=ax)
        ax.set_title("Heatmap: Średnia wartość per miejscówka i kategoria")
        st.pyplot(fig)

    with tabs[3]:
        st.header("Raport interaktywny")
        report_choice = st.selectbox("Wybierz typ raportu", ["Wyniki dla osoby", "Wyniki dla miejscówki"])
        
        if report_choice == "Wyniki dla osoby":
            # Dynamiczne pobieranie listy osób
            persons = sorted(df["person"].unique())
            selected_person = st.selectbox("Wybierz osobę", persons)
            person_df = df[df["person"] == selected_person]
            st.write("Wyniki dla osoby:", selected_person)
            st.dataframe(person_df)
            
            # Uśrednienie wyników dla wybranej osoby wg kategorii
            person_avg = person_df.groupby("category")["value"].mean().reset_index()
            fig, ax = plt.subplots()
            sns.barplot(data=person_avg, x="category", y="value", ax=ax)
            ax.set_title(f"Średnia wartość dla {selected_person}")
            ax.set_xlabel("Kategoria")
            ax.set_ylabel("Średnia wartość")
            st.pyplot(fig)
        else:
            # Dynamiczne pobieranie listy miejscówek
            venues = sorted(df["venue"].unique())
            selected_venue = st.selectbox("Wybierz miejscówkę", venues)
            venue_df = df[df["venue"] == selected_venue]
            st.write("Wyniki dla miejscówki:", selected_venue)
            st.dataframe(venue_df)
            
            # Uśrednienie wyników dla wybranej miejscówki wg kategorii
            venue_avg = venue_df.groupby("category")["value"].mean().reset_index()
            fig, ax = plt.subplots()
            sns.barplot(data=venue_avg, x="category", y="value", ax=ax)
            ax.set_title(f"Średnia wartość dla {selected_venue}")
            ax.set_xlabel("Kategoria")
            ax.set_ylabel("Średnia wartość")
            st.pyplot(fig)
