import streamlit as st
import pandas as pd
import requests

# CSV-Datei laden
@st.cache_data
def load_data():
    return pd.read_csv("./OlympicDataexport2025.csv")

df = load_data()

def get_infobox_image(name):
    """
    Ruft über die MediaWiki-API das Infobox-Bild (Thumbnail) eines Artikels ab.
    """
    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS = {
        "action": "query",
        "titles": name,
        "prop": "pageimages",
        "format": "json",
        "pithumbsize": 500  # Thumbnail-Größe
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
        # Zuerst versuchen wir, Athleten mit Medaillen zu finden
        medal_count = filtered_df[filtered_df["Medal"].notna()].groupby("Name")["Medal"].count()
        if medal_count.empty:
            # Falls keiner Medaillen hat, den ersten Athleten auswählen
            top_athlete = filtered_df.loc[filtered_df["Medal"].isna(), "Name"].iloc[0]
            max_medals = 0
            st.warning("⚠️ Kein Athlet mit Medaillen gefunden. Zeige den ersten Athleten ohne Medaillen.")
        else:
            top_athlete = medal_count.idxmax()
            max_medals = medal_count.max()
            st.success(f"🏆 Erfolgreichster Athlet: **{top_athlete}** mit **{max_medals}** Medaillen!")
        
        # Infobox-Bild über die MediaWiki-API abrufen
        image_url = get_infobox_image(top_athlete)
        if image_url:
            st.image(image_url, caption=top_athlete)
        else:
            st.info("📷 Kein Bild aus der Infobox verfügbar.")
