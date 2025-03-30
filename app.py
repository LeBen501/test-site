import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# CSV-Datei laden
@st.cache_data
def load_data():
    return pd.read_csv("./OlympicDataexport2025.csv")

df = load_data()

def get_wikipedia_image_infobox(name):
    """
    Sucht gezielt das Bild in der Infobox eines Wikipedia-Artikels.
    """
    URL = f"https://en.wikipedia.org/wiki/{name.replace(' ', '_')}"
    response = requests.get(URL)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Suche nach der Infobox, die üblicherweise ein div mit der Klasse "infobox" ist
        infobox = soup.find('table', {'class': 'infobox'})

        if infobox:
            # Suche nach dem ersten <img>-Tag innerhalb der Infobox
            img_tag = infobox.find('img')
            if img_tag:
                img_url = img_tag.get('src')
                if img_url:
                    # Falls die URL mit "//" beginnt, füge "https:" hinzu
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    # Falls die URL mit '/' beginnt, ergänze die Domain von Wikipedia
                    elif img_url.startswith('/'):
                        img_url = 'https://en.wikipedia.org' + img_url
                    return img_url
    return None

st.title("🏅 Finde den erfolgreichsten Athleten!")
st.markdown("Gib Größe, Gewicht und Geschlecht ein, um den erfolgreichsten Athleten zu finden.")

height = st.number_input("Größe (cm):", min_value=100, max_value=250, step=1)
weight = st.number_input("Gewicht (kg):", min_value=30, max_value=200, step=1)
sex = st.selectbox("Geschlecht:", ["M", "F"])

if st.button("🔍 Athlet finden"):
    filtered_df = df[(df["Height"] == height) & (df["Weight"] == weight) & (df["Sex"] == sex)]
    if filtered_df.empty:
        st.warning("❌ Kein passender Athlet gefunden.")
    else:
        medal_count = filtered_df[filtered_df["Medal"].notna()].groupby("Name")["Medal"].count()
        if medal_count.empty:
            top_athlete = filtered_df.loc[filtered_df["Medal"].isna(), "Name"].iloc[0]
            max_medals = 0
            st.warning("⚠️ Kein Athlet mit Medaillen gefunden. Zeige ersten Athleten ohne Medaillen.")
        else:
            top_athlete = medal_count.idxmax()
            max_medals = medal_count.max()
            st.success(f"🏆 Erfolgreichster Athlet: **{top_athlete}** mit **{max_medals}** Medaillen!")
        
        # Bild aus der Infobox abrufen
        image_url = get_wikipedia_image_infobox(top_athlete)
        if image_url:
            st.image(image_url, caption=top_athlete)
        else:
            st.info("📷 Kein Bild aus der Infobox verfügbar.")
