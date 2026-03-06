import streamlit as st
import pandas as pd
from datetime import timedelta

# --- CONFIGURATIE ---
st.set_page_config(page_title="Marathon Schema Generator", layout="wide")

def bereken_tempos(streeftijd_str):
    try:
        h, m, s = map(int, streeftijd_str.split(':'))
        totaal_sec = h * 3600 + m * 60 + s
        m_tempo_sec = totaal_sec / 42.195
        
        return {
            "Easy (E)": m_tempo_sec * 1.22,
            "Marathon (M)": m_tempo_sec,
            "Threshold (T)": m_tempo_sec * 0.92,
            "Interval (I)": m_tempo_sec * 0.88
        }
    except:
        return None

def format_tempo(sec):
    minuten = int(sec // 60)
    seconden = int(sec % 60)
    return f"{minuten}:{seconden:02d} min/km"

# --- UI ---
st.title("🏃 Mijn Persoonlijke Marathon Planner")
st.markdown("Vul je gegevens in en genereer direct een 12-weken schema.")

with st.sidebar:
    st.header("Instellingen")
    doel = st.selectbox("Afstand", ["Marathon", "Halve Marathon"])
    streeftijd = st.text_input("Streeftijd (u:mm:ss)", "03:40:00")
    frequentie = st.slider("Trainingen per week", 3, 5, 4)
    start_datum = st.date_input("Wanneer wil je beginnen?")

tempos = bereken_tempos(streeftijd)

if tempos:
    st.subheader("⏱️ Jouw Trainingstempo's")
    cols = st.columns(4)
    for i, (naam, sec) in enumerate(tempos.items()):
        cols[i].metric(naam, format_tempo(sec))

    # --- SCHEMA LOGICA (Simpel 12-weken model) ---
    st.subheader("📅 Jouw 12-Weken Schema")
    
    schema_data = []
    base_long_run = 15 if doel == "Marathon" else 8
    
    for week in range(1, 13):
        # Progressie: elke week 10% erbij, behalve rustweken (4, 8)
        factor = 1.1 ** (week - 1)
        if week in [4, 8]: factor *= 0.7 
        
        long_run = round(base_long_run * factor)
        # Limiet voor marathon training
        if doel == "Marathon" and long_run > 32: long_run = 32
        
        schema_data.append({
            "Week": week,
            "Maandag": "Rust",
            "Dinsdag": f"Interval: 5x800m @ {format_tempo(tempos['Interval (I)'])}",
            "Woensdag": f"Easy: 8km @ {format_tempo(tempos['Easy (E)'])}",
            "Donderdag": "Rust / Kracht",
            "Vrijdag": f"Tempo: 5km @ {format_tempo(tempos['Threshold (T)'])}",
            "Zaterdag": "Rust",
            "Zondag": f"Lange loop: {long_run}km @ {format_tempo(tempos['Easy (E)'])}"
        })

    df = pd.DataFrame(schema_data)
    st.dataframe(df, use_container_width=True)
    
    # Download knop
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download schema als CSV", csv, "loop-schema.csv", "text/csv")
