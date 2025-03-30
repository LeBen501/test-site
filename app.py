import streamlit as st
import pandas as pd
import requests

# CSV-Datei laden
@st.cache_data
def load_data():
    return pd.read_csv("./OlympicDataexport2025.csv")

df = load_data()

st.title("🏅 Finde den erfolgreichsten Athleten!")
st.markdown(
    "Gib Größe, Gewicht und Geschlecht ein, um den erfolgreichsten Athleten zu finden. "
    "Es werden bevorzugt Athleten angezeigt, die ab 1990 in den Spielen teilgenommen haben. "
    "Zusätzlich erhältst du eine Übersicht, welche Medaillen (inklusive Event, Jahr, Saison und Stadt) "
    "der Athlet gewonnen hat."
)

# Eingabefelder für Nutzer
height = st.number_input("Größe (cm):", min_value=100, max_value=250, step=1)
weight = st.number_input("Gewicht (kg):", min_value=30, max_value=200, step=1)
sex = st.selectbox("Geschlecht:", ["M", "F"])

if st.button("🔍 Athlet finden"):
    # Filtere die Athleten basierend auf den Eingaben
    base_df = df[(df["Height"] == height) & (df["Weight"] == weight) & (df["Sex"] == sex)]
    
    if base_df.empty:
        st.warning("❌ Kein passender Athlet gefunden.")
    else:
        # Priorisiere Athleten, die ab 1990 teilgenommen haben
        prioritized_df = base_df[base_df["Year"].astype(int) >= 1990]
        if prioritized_df.empty:
            prioritized_df = base_df
        
        # Aggregiere die Medaillenanzahl für Athleten, die mindestens eine Medaille haben
        medal_count = prioritized_df[prioritized_df["Medal"].notna()].groupby("Name")["Medal"].count()
        if medal_count.empty:
            # Falls keiner Medaillen hat, wähle den ersten Athleten aus
            top_athlete = prioritized_df.iloc[0]["Name"]
            max_medals = 0
            st.warning("⚠️ Kein Athlet mit Medaillen gefunden. Zeige den ersten Athleten ohne Medaillen.")
        else:
            top_athlete = medal_count.idxmax()
            max_medals = medal_count.max()
            st.success(f"🏆 Erfolgreichster Athlet: **{top_athlete}** mit **{max_medals}** Medaillen!")
        
        # Zusätzliche Details zu den Medaillen (nur die Zeilen mit einer Medaille)
        details_df = prioritized_df[(prioritized_df["Name"] == top_athlete) & (prioritized_df["Medal"].notna())]
        # Optional: sortiere nach Jahr, z.B. aufsteigend
        details_df = details_df.sort_values(by="Year", ascending=True)
        # Wähle relevante Spalten zur Anzeige aus
        display_df = details_df[["Medal", "Event", "Year", "Season", "City"]]
        
        st.markdown("### Übersicht der gewonnenen Medaillen:")
        st.table(display_df.reset_index(drop=True))
        
        # Optional: falls du ein Bild aus Wikipedia zeigen möchtest, kannst du hier noch eine Funktion einbinden
        # (z.B. über die MediaWiki-API, siehe vorherige Beispiele)
        st.info("Hinweis: Es wird kein Bild angezeigt, da diese Funktion hier deaktiviert wurde.")
