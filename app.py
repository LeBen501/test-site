import streamlit as st
import pandas as pd
import requests

@st.cache_data
def load_data():
    return pd.read_csv("./OlympicDataexport2025.csv")

df = load_data()

# Erzeuge eine Spalte 'YearInt' als Integer aus den ersten 4 Zeichen des "Year"-Feldes
df['YearInt'] = df['Year'].apply(lambda x: int(str(x)[:4]) if pd.notna(x) else None)

def get_infobox_image(name):
    """
    Ruft über die MediaWiki-API das Infobox-Bild (Thumbnail) des Artikels ab.
    Falls das zurückgegebene Bild dem Standard-Icon entspricht, wird None zurückgegeben.
    """
    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS = {
        "action": "query",
        "titles": name,
        "prop": "pageimages",
        "format": "json",
        "pithumbsize": 500  # gewünschte Thumbnail-Größe
    }
    response = requests.get(URL, params=PARAMS)
    data = response.json()
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        thumbnail = page.get("thumbnail", {})
        source = thumbnail.get("source")
        if source:
            # Filter: Wenn es das Standard-Wikipedia-Icon ist, verwerfen
            if "wikipedia.org/static/images/icons/wikipedia.png" in source.lower():
                return None
            return source
    return None

# Filter: Nur Athleten, die ab 1990 teilnehmen
filtered_df = df[df['YearInt'] >= 1990]

if filtered_df.empty:
    st.warning("❌ Kein Athlet gefunden, der ab 1990 teilgenommen hat.")
else:
    # Gruppiere nach Name und zähle die Medaillen (nicht-leere "Medal"-Einträge)
    medal_counts = (
        filtered_df.groupby("Name")["Medal"]
        .apply(lambda x: x[x != ""].count())
        .reset_index(name="MedalCount")
    )
    # Für jeden Athleten den Sport (erste Angabe)
    sports = filtered_df.groupby("Name")["Sport"].first().reset_index(name="Sport")
    # Zusammenführen
    athletes = pd.merge(medal_counts, sports, on="Name")
    # Sortieren: Zuerst absteigend nach Medaillen, dann alphabetisch
    athletes_sorted = athletes.sort_values(by=["MedalCount", "Name"], ascending=[False, True])
    top_athlete = athletes_sorted.iloc[0]["Name"]
    top_medals = athletes_sorted.iloc[0]["MedalCount"]
    top_sport = athletes_sorted.iloc[0]["Sport"]
    
    st.success(f"🏆 {top_athlete} ({top_sport}) – Medaillen: {top_medals}")
    
    # Infobox-Bild des Athleten abrufen
    athlete_image = get_infobox_image(top_athlete)
    
    # Zwei Spalten: Links Bild, rechts Textinformationen
    col1, col2 = st.columns(2)
    with col1:
        if athlete_image:
            st.image(athlete_image, caption=top_athlete)
        else:
            st.info("📷 Kein Bild verfügbar.")
    with col2:
        st.markdown(f"**Name:** {top_athlete}")
        st.markdown(f"**Sport:** {top_sport}")
        st.markdown(f"**Medaillen:** {top_medals}")
