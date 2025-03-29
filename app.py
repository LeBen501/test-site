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
        # Wikipedia-Seite mit requests laden
        url = page.fullurl
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Suchen nach allen Bildern auf der Seite
        img_tags = soup.find_all('img')
        
        # Durchsuche alle Bilder und suche nach einem mit den Formaten jpg, jpeg, png
        for img_tag in img_tags:
            img_url = img_tag.get('src')
            if img_url and (img_url.endswith(('jpg', 'jpeg', 'png'))):
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
        # Filtern nach Medaillen und den erfolgreichsten Athleten ermitteln
        medal_count = filtered_df[filtered_df["Medal"].notna()].groupby("Name")["Medal"].count()

        # Wenn kein Athlet mit Medaillen gefunden wurde, zeige einen Athleten ohne Medaille
        if medal_count.empty:
            # In diesem Fall einen Athleten ohne Medaille finden
            top_athlete = filtered_df.loc[filtered_df["Medal"].isna(), "Name"].iloc[0]
            max_medals = 0
            st.warning("⚠️ Kein Athlet mit Medaillen gefunden. Der erste Athlet ohne Medaillen wird angezeigt.")
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
