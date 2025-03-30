import streamlit as st
import pandas as pd
import requests

# CSV-Datei laden
@st.cache_data
def load_data():
    return pd.read_csv("./OlympicDataexport2025.csv")

df = load_data()

def get_wikipedia_image_api(name):
    """
    Ruft über die MediaWiki-API das Bild (Thumbnail) eines Artikels ab.
    """
    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS = {
        "action": "query",
        "titles": name,
        "prop": "pageimages",
        "format": "json",
        "pithumbsize": 500
    }
    response = requests.get(URL, params=PARAMS)
    data = response.json()
    pages = data.get("query", {}).get("pages", {})
    for pageid in pages:
        page = pages[pageid]
        thumbnail = page.get("thumbnail", {})
        source = thumbnail.get("source")
        if source:
            return source
    return None

def get_wikipedia_image_fallback(name):
    """
    Fallback-Methode: Falls die API kein Bild liefert, wird die Wikipedia-Seite per HTML-Scraping untersucht.
    """
    # Ersetze Leerzeichen durch Unterstriche, damit der URL korrekt ist
    URL = f"https://en.wikipedia.org/wiki/{name.replace(' ', '_')}"
    response = requests.get(URL)
    if response.status_code == 200:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        # Suche nach allen <img>-Tags auf der Seite
        img_tags = soup.find_all('img')
        for img_tag in img_tags:
            img_url = img_tag.get('src')
            if img_url and (img_url.endswith(('jpg', 'jpeg', 'png'))):
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = 'https://en.wikipedia.org' + img_url
                return img_url
    return None

def get_wikipedia_image(name):
    # Zuerst versuchen wir, über die MediaWiki-API ein Bild abzurufen
    img = get_wikipedia_image_api(name)
    if img:
        return img
    # Falls die API kein Bild liefert, Fallback zur HTML-Suche
    return get_wikipedia_image_fallback(name)

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
        
        image_url = get_wikipedia_image(top_athlete)
        if image_url:
            st.image(image_url, caption=top_athlete)
        else:
            st.info("📷 Kein Bild verfügbar.")
