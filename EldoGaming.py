import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from firebase_admin import credentials, db
import firebase_admin

st.set_page_config(layout="wide")
st.title(":green-background[Wyjścia Melanże]")
st.caption('Projekt: "Kim Pan Był" v.5  Współfinansowany przez własną kieszeń. Proszę uzupełniać na bieżąco || Skala ocen od 0-7,5')

tab1, tab2 = st.tabs(["Ankieta", "Wykresiki"])

#! Funkcje pomocnicze 
def compute_average_points(answers):
    # Oblicza średnią z punktów dla kategorii (pomijając te, które mają być liczone automatycznie)
    vals = [entry["WARTOŚĆ"] for entry in answers 
            if entry["KATEGORIA"] not in ["ŚREDNIA Z PUNKTÓW", "ŚREDNIA Z MIEJSCÓWKI"]]
    if vals:
        return round(sum(vals) / len(vals),2)
    return 0.0
def compute_average_place(selected_venue):
    # Zbieramy wartości "ŚREDNIA Z PUNKTÓW" dla wszystkich użytkowników, którzy mają wpis dla danej miejscówki.
    values = []
    for person, venues_dict in st.session_state.results.items():
        if selected_venue in venues_dict:
            answers = venues_dict[selected_venue]
            # Wyszukujemy wpis dla "ŚREDNIA Z PUNKTÓW"
            for entry in answers:
                if entry.get("KATEGORIA") == "ŚREDNIA Z PUNKTÓW":
                    values.append(entry.get("WARTOŚĆ", 0.0))
                    break
    if values:
        return round(sum(values) / len(values), 2)
    return 0.0
#!

#? Funkcja dialogowa do edycji odpowiedzi
@st.dialog("Edytuj odpowiedzi", width="small")
def edit_answers():
    current_answers = st.session_state.results[selected_person][selected_venue]
    new_answers = {}
    with st.form(key="survey_edit_form"):
        for entry in current_answers:
            cat = entry["KATEGORIA"]
            # Jeśli kategoria to "ŚREDNIA Z PUNKTÓW" lub "ŚREDNIA Z MIEJSCÓWKI",
            # pomijamy tworzenie suwaka i zachowujemy dotychczasową wartość.
            if cat in ["ŚREDNIA Z PUNKTÓW", "ŚREDNIA Z MIEJSCÓWKI"]:
                new_answers[cat] = entry["WARTOŚĆ"]
            else:
                default_val = float(entry["WARTOŚĆ"]) if isinstance(entry["WARTOŚĆ"], (int, float)) else 0.0
                new_value = st.slider(
                    f":green-background[{cat}]",
                    min_value=0.0,
                    max_value=7.5,
                    value=default_val,
                    step=0.5,
                    format="%.1f",
                    label_visibility="visible",
                )
                new_answers[cat] = new_value

        submitted = st.form_submit_button("Zapisz zmiany")
        if submitted:
            # Aktualizacja wyników w st.session_state dla wybranej pary
            st.session_state.results[selected_person][selected_venue] = [
                {"KATEGORIA": cat, "WARTOŚĆ": new_answers[cat]} for cat in categories
            ]
            st.success("Odpowiedzi zaktualizowane!")
            # Aktualizacja tylko danego węzła w Firebase
            node_ref = db.reference(f'results/{selected_person}/{selected_venue}')
            node_ref.set(st.session_state.results[selected_person][selected_venue])
            st.rerun()  # Zamknięcie dialogu i odświeżenie aplikacji

with tab1:
    # Lista opcji
    persons = ("Bartek", "Maciek", "Bacper", "Darek")
    venues = ("SKUNSTREFA", "PIZZA", "KFC")
    categories = [
        "FOOD", 
        "WYSTRÓJ", 
        "OBSŁUGA", 
        "PERFORMANCE PER PRICE", 
        "INNE", 
        "ŚREDNIA Z PUNKTÓW", 
        "ŚREDNIA Z MIEJSCÓWKI"
    ]

    selected_person = st.selectbox(":green-background[Wybierz osobę]", persons)
    selected_venue = st.selectbox(":green-background[Wybierz miejscówkę]", venues)

    # Inicjalizacja stanu aplikacji – jeśli już istnieje, nie nadpisujemy go
    if "results" not in st.session_state:
        st.session_state.results = {}

    # Dla wybranej osoby i miejscówki pobieramy dane z Firebase tylko, jeśli nie ma ich już w st.session_state
    if selected_person not in st.session_state.results:
        st.session_state.results[selected_person] = {}
    if selected_venue not in st.session_state.results[selected_person]:
        ref = db.reference(f'results/{selected_person}/{selected_venue}')
        fetched_data = ref.get()
        if fetched_data:
            st.session_state.results[selected_person][selected_venue] = fetched_data
        else:
            st.session_state.results[selected_person][selected_venue] = [{"KATEGORIA": cat, "WARTOŚĆ": 0.0} for cat in categories]

    current_answers = st.session_state.results[selected_person][selected_venue]
    # Aktualizacja "ŚREDNIA Z PUNKTÓW" dla bieżącej pary (dla danego użytkownika)
    avg_punkty = compute_average_points(current_answers)
    updated = False
    for entry in current_answers:
        if entry["KATEGORIA"] == "ŚREDNIA Z PUNKTÓW":
            entry["WARTOŚĆ"] = avg_punkty
            updated = True
            break
    if not updated:
        current_answers.append({"KATEGORIA": "ŚREDNIA Z PUNKTÓW", "WARTOŚĆ": avg_punkty})

    # Obliczenie "ŚREDNIA Z MIEJSCÓWKI" jako średniej z "ŚREDNIA Z PUNKTÓW" dla wszystkich użytkowników (dla danej miejscówki)
    avg_miejscowka = compute_average_place(selected_venue)
    updated_place = False
    for entry in current_answers:
        if entry["KATEGORIA"] == "ŚREDNIA Z MIEJSCÓWKI":
            entry["WARTOŚĆ"] = avg_miejscowka
            updated_place = True
            break
    if not updated_place:
        current_answers.append({"KATEGORIA": "ŚREDNIA Z MIEJSCÓWKI", "WARTOŚĆ": avg_miejscowka})

    # Przycisk otwierający okno dialogowe do edycji
    if st.button(":rainbow[Edytuj odpowiedzi]"):
        edit_answers()


    # Budowanie finalnego DataFrame tylko dla wybranej pary
    rows = []
    for entry in current_answers:
        rows.append({
            "KATEGORIA": entry["KATEGORIA"],
            "WARTOŚĆ": entry["WARTOŚĆ"]
        })
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
                    max_value=7.5,  # Ustaw odpowiedni zakres – tu przykład do 7.5
                ),
            },
            hide_index=True,
            disabled=["KATEGORIA"],
            )

with tab2:
    # Zbieranie wszystkich danych z session_state
    rows = []
    for person, venues_dict in st.session_state.results.items():
        for venue, answers_list in venues_dict.items():
            for entry in answers_list:
                rows.append({
                    "OSOBA": person,
                    "MIEJSCÓWKA": venue,
                    "KATEGORIA": entry["KATEGORIA"],
                    "WARTOŚĆ": entry["WARTOŚĆ"]
                })

    if rows:
        df_all = pd.DataFrame(rows)
        st.subheader("Pełny DataFrame z wynikami")
        st.dataframe(df_all)
        # Wykres - średnia wartość dla każdej kategorii
        avg_values = df_all.groupby("KATEGORIA")["WARTOŚĆ"].mean().reset_index()
        st.subheader("Średnia wartość dla każdej kategorii")
        fig, ax = plt.subplots()
        sns.barplot(x="KATEGORIA", y="WARTOŚĆ", data=avg_values, ax=ax)
        ax.set_title("Średnia ocena dla każdej kategorii")
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # Wykres - średnia wartość dla każdej osoby
        avg_person_values = df_all.groupby("OSOBA")["WARTOŚĆ"].mean().reset_index()
        st.subheader("Średnia wartość dla każdej osoby")
        fig, ax = plt.subplots()
        sns.barplot(x="OSOBA", y="WARTOŚĆ", data=avg_person_values, ax=ax)
        ax.set_title("Średnia ocena dla każdej osoby")
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # Wykres - średnia wartość dla każdej miejscówki
        avg_venue_values = df_all.groupby("MIEJSCÓWKA")["WARTOŚĆ"].mean().reset_index()
        st.subheader("Średnia wartość dla każdej miejscówki")
        fig, ax = plt.subplots()
        sns.barplot(x="MIEJSCÓWKA", y="WARTOŚĆ", data=avg_venue_values, ax=ax)
        ax.set_title("Średnia ocena dla każdej miejscówki")
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.info("Brak wyników do analizy.")