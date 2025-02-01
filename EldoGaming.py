import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
st.set_page_config(layout="wide")
st.title(":green-background[Wyjścia Melanże]")

tab1, tab2 = st.tabs(["Ankieta","Wykresiki"])

with tab1:
    # Lista osób, miejscówek oraz kategorii ankiety
    persons = ("Bartek", "Maciek", "Bacper")
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


    def default_survey():
        return [{"KATEGORIA": cat, "WARTOŚĆ": 0.0} for cat in categories]

    if "results" not in st.session_state:
        st.session_state.results = {
            person: {venue: default_survey() for venue in venues}
            for person in persons
        }

    selected_person = st.selectbox("Wybierz osobę", persons)
    selected_venue = st.selectbox("Wybierz miejscówkę", venues)

    # Upewniamy się, że dla wybranej pary mamy już dane
    if st.session_state.results[selected_person][selected_venue] is None:
        st.session_state.results[selected_person][selected_venue] = default_survey()

    # Pobieramy aktualne dane dla wybranej pary
    current_answers = st.session_state.results[selected_person][selected_venue]

    # Expander do edycji odpowiedzi
    with st.expander("Edytuj odpowiedzi"):
        with st.form(key="survey_edit_form"):
            new_answers = {}
            for entry in current_answers:
                cat = entry["KATEGORIA"]
                # Używamy aktualnej wartości z DataFrame jako domyślnej w number_input
                new_value = st.slider(
                    f"Wartość dla kategorii: {cat}",
                    min_value=0.0,
                    max_value=7.5,
                    value=entry["WARTOŚĆ"],  # Domyślnie bierze wartość z DataFrame
                    step=0.5,
                    format="%.1f"
                )
                new_answers[cat] = new_value
            submitted = st.form_submit_button("Zapisz zmiany")
            if submitted:
                # Aktualizujemy wyniki dla wybranej osoby i miejscówki
                st.session_state.results[selected_person][selected_venue] = [
                    {"KATEGORIA": cat, "WARTOŚĆ": new_answers[cat]} for cat in categories
                ]
                st.success("Odpowiedzi zaktualizowane!")
                st.rerun()  # Odświeżenie strony, aby pokazać zmiany

    # Budujemy finalny DataFrame ze wszystkich wyników tylko dla wybranej osoby i miejscówki
    rows = []
    for person, venues_dict in st.session_state.results.items():
        if person == selected_person:  # Filtrujemy po wybranej osobie
            for venue, answers_list in venues_dict.items():
                if venue == selected_venue:  # Filtrujemy po wybranej miejscówce
                    # Jeśli answers_list jest None, inicjujemy domyślne dane
                    if answers_list is None:
                        answers_list = default_survey()
                        st.session_state.results[person][venue] = answers_list
                    for entry in answers_list:
                        rows.append({
                            "OSOBA": person,
                            "MIEJSCÓWKA": venue,
                            "KATEGORIA": entry["KATEGORIA"],
                            "WARTOŚĆ": entry["WARTOŚĆ"]
                        })

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df)
    else:
        st.info("Brak wyników ankiety dla wybranej osoby i miejscówki.")

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
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        st.pyplot(fig)

        # Wykres - średnia wartość dla każdej osoby
        avg_person_values = df_all.groupby("OSOBA")["WARTOŚĆ"].mean().reset_index()
        st.subheader("Średnia wartość dla każdej osoby")
        fig, ax = plt.subplots()
        sns.barplot(x="OSOBA", y="WARTOŚĆ", data=avg_person_values, ax=ax)
        ax.set_title("Średnia ocena dla każdej osoby")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        st.pyplot(fig)

        # Wykres - średnia wartość dla każdej miejscówki
        avg_venue_values = df_all.groupby("MIEJSCÓWKA")["WARTOŚĆ"].mean().reset_index()
        st.subheader("Średnia wartość dla każdej miejscówki")
        fig, ax = plt.subplots()
        sns.barplot(x="MIEJSCÓWKA", y="WARTOŚĆ", data=avg_venue_values, ax=ax)
        ax.set_title("Średnia ocena dla każdej miejscówki")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        st.pyplot(fig)
    else:
        st.info("Brak wyników do analizy.")