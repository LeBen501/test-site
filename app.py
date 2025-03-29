import streamlit as st
import pandas as pd

# CSV-Datei laden
@st.cache_data
def load_data():
    return pd.read_csv("./athletes.csv")

df = load_data()

# Titel der App
st.title("🏅 Finde den erfolgreichsten Athleten!")

# Eingabefelder für Nutzer
height = st.number_input("Größe (cm):", min_value=100, max_value=250, step=1)
weight = st.number_input("Gewicht (kg):", min_value=30, max_value=200, step=1)
sex = st.selectbox("Geschlecht:", ["M", "F"])

# Button für Suche
if st.button("Athlet finden"):
    # Filtern nach Größe, Gewicht und Geschlecht
    filtered_df = df[(df["Height"] == height) & (df["Weight"] == weight) & (df["Sex"] == sex)]
    
    if filtered_df.empty:
        st.warning("Kein passender Athlet gefunden.")
    else:
        # Erfolgreichsten Athleten mit den meisten Medaillen finden
        medal_count = filtered_df[filtered_df["Medal"].notna()].groupby("Name")["Medal"].count()
        
        if medal_count.empty:
            st.warning("Kein passender Athlet mit Medaillen gefunden.")
        else:
            top_athlete = medal_count.idxmax()
            max_medals = medal_count.max()
            st.success(f"🏆 Erfolgreichster Athlet: **{top_athlete}** mit **{max_medals}** Medaillen!")
