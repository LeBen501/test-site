import streamlit as st
import pandas as pd
import wikipediaapi
import requests
from bs4 import BeautifulSoup

# CSV-Datei laden
@st.cache_data
def load_data():
    return pd.read_csv("./OlympicDataexport2025.csv")

df = load_data()

# Funktion zum Abrufen des Wikipedia-Bildes
def get_wikipedia_image(name):
    wiki_wiki = wikipediaapi.Wikipedia(language='en', user_agent="AthleteFinderApp (suberio.01.11@gmail.com)") 
    page = wiki_wiki.page(name)
    
    if page.exists():
        # Wir müssen die Wikipedia-Seite mit requests laden, um Bilder zu extrahieren
        url = page.fullurl
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Suche nach dem ersten Bild auf der Seite, das im HTML Tag <img> enthalten ist
        img_tag = soup.find('img')
        
        if img_tag:
            img_url = img_tag['src']
            # Bild-URL ggf. anpassen
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif img_url.startswith('/'):
                img_url = 'https://en.wikipedia.org' + img_url
            return img_url
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
                st.image(image_url, caption=top_athlete)
            else:
                st.info("📷 Kein Bild verfügbar.")

