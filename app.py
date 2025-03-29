import streamlit as st
import pandas as pd
import wikipediaapi

# CSV-Datei laden
@st.cache_data
def load_data():
    return pd.read_csv("./OlympicDataexport2025.csv")

df = load_data()

# Funktion zum Abrufen des Wikipedia-Bildes
def get_wikipedia_image(name):
    # Spezifizieren eines benutzerdefinierten User-Agent
    wiki_wiki = wikipediaapi.Wikipedia(language='en', user_agent="AthleteFinderApp (suberio.01.11@gmail.com)") 
    page = wiki_wiki.page(name)
    if page.exists():
        for image in page.images:
            if image.endswith(('jpg', 'jpeg', 'png')):
                return image
    return None

# Titel der App
st.title("🏅 Finde den erfolgreichsten Athleten!")
st.markdown("Gib Größe, Gewicht und Geschlecht ein, um den erfolgreichsten Athleten zu finden.")

# Eingabefelder für Nutzer
height = st.number_input("Größe (cm):", min_value=100, max_value=250, step=1)
weight = st.number_input("Gewicht (kg):", min_value=30, max_value=200, step=1)
sex = st.selectbox("Geschlecht:", ["M", "F"])

# Button für Suche
if st.button("🔍 Athlet finden"):
    filtered_df = df[(df["Height"] == height) & (df["Weight"] == weight) & (df["Sex"] == sex)]
    
    if filtered_df.empty:
        st.warning("❌ Kein passender Athlet gefunden.")
    else:
        medal_count = filtered_df[filtered_df["Medal"].notna()].groupby("Name")["Medal"].count()
        
        if medal_count.empty:
            st.warning("⚠️ Kein passender Athlet mit Medaillen gefunden.")
        else:
            top_athlete = medal_count.idxmax()
            max_medals = medal_count.max()
            st.success(f"🏆 Erfolgreichster Athlet: **{top_athlete}** mit **{max_medals}** Medaillen!")
            
            # Wikipedia-Bild abrufen und anzeigen
            image_url = get_wikipedia_image(top_athlete)
            if image_url:
                st.image(image_url, caption=top_athlete, use_column_width=True)
            else:
                st.info("📷 Kein Bild verfügbar.")
