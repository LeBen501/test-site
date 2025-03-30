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
        "pithumbsize": 500
    }
    response = requests.get(URL, params=PARAMS)
    data = response.json()
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        thumbnail = page.get("thumbnail", {})
        source = thumbnail.get("source")
        if source:
            # Filtere das Standard-Wikipedia-Icon heraus
            if "wikipedia.org/static/images/icons/wikipedia.png" in source.lower():
                return None
            return source
    return None

st.title("🏅 Finde den erfolgreichsten Athleten!")
st.markdown(
    "Gib Größe, Gewicht und Geschlecht ein, um den erfolgreichsten Athleten zu finden. "
    "Es werden bevorzugt Athleten angezeigt, die ab 1990 in den Spielen teilgenommen haben."
)

# Eingabefelder für Nutzer
height = st.number_input("Größe (cm):", min_value=100, max_value=250, step=1)
weight = st.number_input("Gewicht (kg):", min_value=30, max_value=200, step=1)
sex = st.selectbox("Geschlecht:", ["M", "F"])

if st.button("🔍 Athlet finden"):
    # Filtere Athleten basierend auf Eingaben
    base_df = df[(df["Height"] == height) & (df["Weight"] == weight) & (df["Sex"] == sex)]
    
    if base_df.empty:
        st.warning("❌ Kein passender Athlet gefunden.")
    else:
        # Priorisierung: Athleten mit Year >= 1990
        prioritized_df = base_df[base_df["Year"].astype(int) >= 1990]
        if prioritized_df.empty:
            prioritized_df = base_df  # Fallback, falls keiner ab 1990 dabei ist
        
        # Aggregiere Medaillen: Zähle Zeilen, in denen "Medal" nicht leer ist
        medal_count = prioritized_df[prioritized_df["Medal"].notna()].groupby("Name")["Medal"].count()
        
        if medal_count.empty:
            # Falls keiner Medaillen hat, wähle den ersten Athleten aus
            top_athlete = prioritized_df.iloc[0]["Name"]
            max_medals = 0
            st.success(f"🏆 {top_athlete} (Keine Medaillen)")
        else:
            top_athlete = medal_count.idxmax()
            max_medals = medal_count.max()
            st.success(f"🏆 {top_athlete} mit {max_medals} Medaillen")
        
        # Bestimme die Disziplin (Sport) des ausgewählten Athleten
        sport = prioritized_df.loc[prioritized_df["Name"] == top_athlete, "Sport"].iloc[0]
        st.markdown(f"**Disziplin:** {sport}")
        
        # Wenn Medaillendetails vorhanden, zeige diese als Tabelle an
        details_df = prioritized_df[(prioritized_df["Name"] == top_athlete) & (prioritized_df["Medal"].notna())]
        if not details_df.empty:
            details_df = details_df.sort_values(by="Year", ascending=True)
            display_df = details_df[["Medal", "Event", "Year", "Season", "City"]]
            st.markdown("### Übersicht der gewonnenen Medaillen:")
            st.table(display_df.reset_index(drop=True))
        else:
            st.info("Keine Medaillendetails verfügbar.")
        
        # Optional: Infobox-Bild aus Wikipedia abrufen
        image_url = get_infobox_image(top_athlete)
        if image_url:
            st.image(image_url, caption=top_athlete)
        else:
            st.info("📷 Kein Bild aus der Infobox verfügbar.")
