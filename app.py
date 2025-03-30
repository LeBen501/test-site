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
    und filtert Standard-Icons heraus.
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
    for page in pages.values():
        thumbnail = page.get("thumbnail", {})
        source = thumbnail.get("source")
        if source:
            # Filtere Standard-Icons heraus:
            if "wikipedia.org/static/images/icons/wikipedia.png" in source.lower():
                return None
            return source
    return None

# Mapping: Sport -> Icon-URL (Beispiele – passe die URLs nach Bedarf an)
sports_icons = {
    "Basketball": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Basketball_icon.svg/50px-Basketball_icon.svg.png",
    "Judo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Judo.svg/50px-Judo.svg.png",
    "Football": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Soccer_ball.svg/50px-Soccer_ball.svg.png",
    "Tug-Of-War": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Tug_of_war.svg/50px-Tug_of_war.svg.png",
    "Speed Skating": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Speed_skating.svg/50px-Speed_skating.svg.png"
}
default_sport_icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Question_mark.svg/50px-Question_mark.svg.png"

st.title("🏅 Finde den erfolgreichsten Athleten!")
st.markdown("Gib Größe, Gewicht und Geschlecht ein, um den erfolgreichsten Athleten zu finden. Es werden bevorzugt Athleten angezeigt, die ab 1990 in den Spielen teilgenommen haben.")

# Eingabefelder für Nutzer
height = st.number_input("Größe (cm):", min_value=100, max_value=250, step=1)
weight = st.number_input("Gewicht (kg):", min_value=30, max_value=200, step=1)
sex = st.selectbox("Geschlecht:", ["M", "F"])

if st.button("🔍 Athlet finden"):
    # Filtere anhand der Eingaben
    base_df = df[(df["Height"] == height) & (df["Weight"] == weight) & (df["Sex"] == sex)]
    
    if base_df.empty:
        st.warning("❌ Kein passender Athlet gefunden.")
    else:
        # Versuche, Athleten aus Jahren >= 1990 zu priorisieren:
        prioritized_df = base_df[base_df["Year"].astype(int) >= 1990]
        if prioritized_df.empty:
            prioritized_df = base_df  # Fallback: alle Athleten
        
        # Aggregiere Medaillen (Zähle die Anzahl der Zeilen mit nicht-leeren "Medal"-Werten)
        medal_count = prioritized_df[prioritized_df["Medal"].notna()].groupby("Name")["Medal"].count()
        if medal_count.empty:
            # Falls keiner Medaillen hat, wähle den ersten Athleten aus dem priorisierten DataFrame
            top_athlete = prioritized_df.iloc[0]["Name"]
            max_medals = 0
        else:
            top_athlete = medal_count.idxmax()
            max_medals = medal_count.max()
        
        # Hole zusätzlich die Sportart für den ausgewählten Athleten (verwende den ersten Treffer)
        sport = prioritized_df.loc[prioritized_df["Name"] == top_athlete, "Sport"].iloc[0]
        
        # Anzeige: Name, Sport und Medaillenzahl
        st.success(f"🏆 **{top_athlete}**\n\n**Sport:** {sport}\n\n**Medaillen:** {max_medals}")
        
        # Athletenbild aus Wikipedia (Infobox-Bild)
        athlete_image = get_infobox_image(top_athlete)
        # Icon für die Sportart
        sport_icon = sports_icons.get(sport, default_sport_icon)
        
        # Zeige beide Bilder nebeneinander an:
        col1, col2 = st.columns(2)
        with col1:
            if athlete_image:
                st.image(athlete_image, caption=top_athlete)
            else:
                st.info("📷 Kein Athletenbild verfügbar.")
        with col2:
            st.image(sport_icon, caption=sport)
