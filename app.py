import streamlit as st
import pandas as pd
from datetime import timedelta, date

# --- CONFIGURATIE ---
st.set_page_config(page_title="Marathon Schema Pro", layout="wide", page_icon="🏃")

def bereken_tempos(streeftijd_str):
    try:
        # Omzetten van u:mm:ss naar totale seconden per km
        h, m, s = map(int, streeftijd_str.split(':'))
        totaal_sec = h * 3600 + m * 60 + s
        m_tempo_sec = totaal_sec / 42.195
        
        return {
            "Easy (E)": m_tempo_sec * 1.22,      # Rustig hersteltempo
            "Marathon (M)": m_tempo_sec,        # Het beoogde wedstrijdtempo
            "Threshold (T)": m_tempo_sec * 0.92, # 'Comfortabel zwaar' (drempel)
            "Interval (I)": m_tempo_sec * 0.88   # Kort en krachtig
        }
    except Exception:
        return None

def format_tempo(sec):
    minuten = int(sec // 60)
    seconden = int(sec % 60)
    return f"{minuten}:{seconden:02d} min/km"

# --- UI HEADER ---
st.title("🏃 Mijn Persoonlijke Marathon Planner")
st.markdown("Dit schema bouwt progressief op en werkt terug vanaf jouw wedstrijddatum.")

# --- SIDEBAR INSTELLINGEN ---
with st.sidebar:
    st.header("⚙️ Instellingen")
    doel = st.selectbox("Afstand", ["Marathon", "Halve Marathon"])
    streeftijd = st.text_input("Streeftijd (u:mm:ss)", "03:40:00")
    wedstrijd_datum = st.date_input("Datum van de wedstrijd", date(2026, 6, 1))
    frequentie = st.slider("Trainingen per week", 3, 5, 4)
    st.info("Het schema wordt berekend over een periode van 12 weken.")

tempos = bereken_tempos(streeftijd)

if tempos:
    # Bereken de startdatum (12 weken voor de wedstrijd, startend op een maandag)
    start_datum_ruw = wedstrijd_datum - timedelta(weeks=12)
    start_datum_maandag = start_datum_ruw - timedelta(days=start_datum_ruw.weekday())
    
    st.success(f"Je 12-weekse schema start op maandag: **{start_datum_maandag.strftime('%d-%m-%Y')}**")

    # --- TEMPO SECTIE ---
    st.subheader("⏱️ Jouw Trainingstempo's")
    cols = st.columns(4)
    zones = list(tempos.items())
    for i, (naam, sec) in enumerate(zones):
        cols[i].metric(naam, format_tempo(sec))

    # --- SCHEMA GENERATIE ---
    schema_data = []
    long_run_history = [] # Voor de grafiek
    
    for week in range(1, 13):
        # Periodisering bepalen
        if week <= 4:
            fase = "Base (Opbouw)"
            lr_km = 12 + (week * 2) if doel == "Marathon" else 8 + week
            interval = f"6x400m @ {format_tempo(tempos['Interval (I)'])}"
        elif week <= 8:
            fase = "Build (Kracht)"
            lr_km = 20 + ((week-4) * 3) if doel == "Marathon" else 12 + (week-4)*2
            interval = f"5x1000m @ {format_tempo(tempos['Threshold (T)'])}"
        elif week <= 10:
            fase = "Peak (Specifiek)"
            lr_km = 30 if week == 9 else 32
            if doel == "Halve Marathon": lr_km = 18 if week == 9 else 20
            interval = f"4x2km @ {format_tempo(tempos['Marathon (M)'])}"
        else:
            fase = "Taper (Gas terug)"
            lr_km = 18 if week == 11 else 10 # Drastische verlaging voor herstel
            interval = "4x400m vlot (wedstrijdprikkel)"

        long_run_history.append(lr_km)
        maandag_datum = start_datum_maandag + timedelta(weeks=week-1)

        week_schema = {
            "Week": week,
            "Datum (Ma)": maandag_datum.strftime('%d-%m'),
            "Fase": fase,
            "Dinsdag (Snelheid)": interval,
            "Woensdag (Easy)": f"{8 if week < 7 else 12}km @ {format_tempo(tempos['Easy (E)'])}",
            "Vrijdag (Tempo)": f"{round(5 + week*0.6)}km @ {format_tempo(tempos['Threshold (T)'])}",
            "Zondag (Long Run)": f"{lr_km}km @ {format_tempo(tempos['Easy (E)'])}"
        }
        schema_data.append(week_schema)

    # --- VISUALISATIE ---
    df = pd.DataFrame(schema_data)
    
    st.subheader("📊 Volume Visualisatie")
    df_grafiek = pd.DataFrame({
        "Week": range(1, 13), 
        "Afstand Lange Loop (km)": long_run_history
    }).set_index("Week")
    st.line_chart(df_grafiek)

    st.subheader("📅 Jouw Volledige Trainingsschema")
    st.dataframe(df, use_container_width=True)
    
    # Download knop
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download schema als CSV",
        data=csv,
        file_name=f"marathon_schema_{streeftijd.replace(':','-')}.csv",
        mime="text/csv",
    )
else:
    st.error("Voer een geldige tijd in (u:mm:ss), bijvoorbeeld 03:40:00")
