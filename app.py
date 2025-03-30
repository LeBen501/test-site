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
    Ruft über die MediaWiki-API das Infobox-Bild (Thumbnail) eines Artikels ab
    und filtert Standard-Icon-Bilder heraus.
    """
    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS = {
        "action": "query",
        "titles": name,
        "prop": "pageimages",
        "format": "json",
        "pithumbsize": 500  # gewünschte Thumbnail-Größe in Pixeln
    }
    response = requests.get(URL, params=PARAMS)
    data = response.json()
    pages = data.get("query", {}).get("pages", {})
    for pageid, page in pages.items():
        thumbnail = page.get("thumbnail", {})
        source = thumbnail.get("source")
        if source:
            # Wenn das zurückgegebene Bild dem Standard-Icon entspricht, verwerfen wir es.
            if "wikipedia.org/static/images/icons/wikipedia.png" in source.lower():
                return None
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
        medal_count = filtered_df[filtered_df["Medal"].notna()].groupby("Name")["Medal"].count()
        if medal_count.empty:
            top_athlete = filtered_df.loc[filtered_df["Medal"].isna(), "Name"].iloc[0]
            max_medals = 0
            st.warning("⚠️ Kein Athlet mit Medaillen gefunden. Zeige den ersten Athleten ohne Medaillen.")
        else:
            top_athlete = medal_count.idxmax()
            max_medals = medal_count.max()
            st.success(f"🏆 Erfolgreichster Athlet: **{top_athlete}** mit **{max_medals}** Medaillen!")
        
        image_url = get_infobox_image(top_athlete)
        if image_url:
            st.image(image_url, caption=top_athlete)
        else:
            st.info("📷 Kein geeignetes Bild gefunden.")
