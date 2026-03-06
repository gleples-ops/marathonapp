import streamlit as st
import pandas as pd
from datetime import timedelta, date

st.set_page_config(page_title="Marathon Schema Pro", layout="wide")

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
    except: return None

def format_tempo(sec):
    minuten = int(sec // 60)
    seconden = int(sec % 60)
    return f"{minuten}:{seconden:02d} min/km"

st.title("🏃 Mijn Persoonlijke Marathon Planner")

with st.sidebar:
    st.header("Instellingen")
    doel = st.selectbox("Afstand", ["Marathon", "Halve Marathon"])
    streeftijd = st.text_input("Streeftijd (u:mm:ss)", "03:40:00")
    # NIEUW: Wedstrijddatum ipv startdatum
    wedstrijd_datum = st.date_input("Datum van de wedstrijd", date(2026, 6, 1))
    frequentie = st.slider("Trainingen per week", 3, 5, 4)

tempos = bereken_tempos(streeftijd)

if tempos:
    # Bereken de startdatum (12 weken voor de wedstrijd)
    start_datum = wedstrijd_datum - timedelta(weeks=12)
    st.info(f"Je schema van 12 weken start op maandag: {(start_datum - timedelta(days=start_datum.weekday())).strftime('%d-%m-%Y')}")

    st.subheader("⏱️ Jouw Trainingstempo's")
    cols = st.columns(4)
    for i, (naam, sec) in enumerate(tempos.items()):
        cols[i].metric(naam, format_tempo(sec))

    schema_data = []
    
    # LOGICA VOOR OPBOUW (Periodisering)
    for week in range(1, 13):
        # Fase bepaling
        if week <= 4: fase = "Base (Opbouw)"
        elif week <= 8: fase = "Build (Kracht)"
        elif week <= 10: fase = "Peak (Specifiek)"
        else: fase = "Taper (Rust)"

        # Dynamische afstanden op basis van week en fase
        if fase == "Base (Opbouw)":
            long_run_km = 12 + (week * 2)
            interval = f"6x400m @ {format_tempo(tempos['Interval (I)'])}"
        elif fase == "Build (Kracht)":
            long_run_km = 20 + ((week-4) * 3)
            interval = f"5x1000m @ {format_tempo(tempos['Threshold (T)'])}"
        elif fase == "Peak (Specifiek)":
            long_run_km = 30 if week == 9 else 32
            interval = f"4x2km @ {format_tempo(tempos['Marathon (M)'])}"
        else: # Taper
            long_run_km = 20 if week == 11 else 10
            interval = "Korte versnellingen"

        # Bereken de maandag van die specifieke week
        maandag_datum = (start_datum - timedelta(days=start_datum.weekday())) + timedelta(weeks=week-1)

        week_schema = {
            "Week": week,
            "Datum (Ma)": maandag_datum.strftime('%d-%m'),
            "Fase": fase,
            "Dinsdag (Interval)": interval,
            "Woensdag (Easy)": f"{8 if week < 8 else 12}km @ {format_tempo(tempos['Easy (E)'])}",
            "Vrijdag (Tempo)": f"{round(5 + week*0.5)}km @ {format_tempo(tempos['Threshold (T)'])}",
            "Zondag (Long Run)": f"{long_run_km}km @ {format_tempo
