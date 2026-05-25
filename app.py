import streamlit as st
import pandas as pd
from agent import FlightOptimizationAgent

# Seiteneinstellungen für das Dashboard
st.set_page_config(
    page_title="Flughafen Analyseplattform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Individuelles CSS für ein modernes Design
st.markdown("""
    <style>
    .reportview-container {
        background: #0f172a;
    }
    .metric-container {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 20px;
    }
    .agent-box {
        background-color: #0f172a;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #3b82f6;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Plattform für Flugrouten Optimierung")
st.write("Diese Plattform analysiert Auslastungen und schlägt Massnahmen zur Umsatzsteigerung vor.")

# Sidebar mit Steuerungselementen
with st.sidebar:
    st.header("Steuerung")
    if st.button("🔄 Daten neu laden"):
        # Cache leeren und neu laden
        for key in ["flights_with_kpis", "analysis_result"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    st.divider()
    st.caption("Datenbank: flughafendb_large")
    st.caption("Zeitraum: 1.–7. Juni 2015")

# Agent einmalig initialisieren und in Session speichern
if "agent" not in st.session_state:
    st.session_state.agent = FlightOptimizationAgent()

agent = st.session_state.agent

try:
    # Flugdaten nur beim ersten Laden abfragen (Cache)
    if "flights_with_kpis" not in st.session_state:
        with st.spinner("Flugdaten werden aus der Datenbank geladen..."):
            flights = agent.fetch_flight_data()
            st.session_state.flights_with_kpis = agent.calculate_kpis(flights)
    
    flights_with_kpis = st.session_state.flights_with_kpis
    df = pd.DataFrame(flights_with_kpis)
    
    # Anzeige der aktuellen KPIs in Spalten
    col1, col2, col3 = st.columns(3)
    
    avg_load = df["load_factor"].mean()
    total_rev = df["revenue"].sum()
    total_passengers = df["passenger_count"].sum()
    
    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric(
            label="Durchschnittliche Auslastung",
            value=f"{avg_load:.1f}%"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric(
            label="Gesamtumsatz Route",
            value=f"{total_rev:,.2f} CHF"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col3:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric(
            label="Passagiere Gesamt",
            value=int(total_passengers)
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Tabelle der Flüge anzeigen
    st.subheader("Aktuelle Flugdaten (Top 5 unterbelegte Flüge)")
    
    # Spaltennamen anpassen für die Anzeige
    display_df = df.rename(columns={
        "id": "ID",
        "flightno": "Flugnummer",
        "route": "Route",
        "departure_time": "Abflugszeit",
        "capacity": "Kapazität",
        "passenger_count": "Passagiere",
        "ticket_price": "Durchschnittspreis CHF",
        "load_factor": "Auslastung %",
        "revenue": "Umsatz CHF"
    })
    
    st.dataframe(display_df, use_container_width=True)

    # Agenten-Analyse
    st.subheader("Analyse und Empfehlungen")
    
    col_analysis_1, col_analysis_2 = st.columns([3, 1])
    
    with col_analysis_2:
        if st.button("🔍 Neue Analyse anfordern"):
            if "analysis_result" in st.session_state:
                del st.session_state["analysis_result"]
            st.rerun()
    
    with col_analysis_1:
        if "analysis_result" not in st.session_state:
            with st.spinner("KI-Analyse wird durchgeführt... Dies kann bis zu 2 Minuten dauern."):
                st.session_state.analysis_result = agent.generate_analysis(flights_with_kpis)
        
        analysis_result = st.session_state.analysis_result
        
        # Kennzeichnung ob LLM oder Fallback
        if "Regelbasierte Analyse" in analysis_result:
            st.info("ℹ️ LLM nicht erreichbar – es wird eine regelbasierte Analyse der echten Daten angezeigt.")
        else:
            st.success("✅ LLM-gestützte Analyse")
        
        st.markdown('<div class="agent-box">', unsafe_allow_html=True)
        st.write(analysis_result)
        st.markdown('</div>', unsafe_allow_html=True)

    # Interaktiver Bereich für die Optimierungsmassnahme
    st.subheader("Aktionen zur Optimierung")
    
    # Auswahl des Flugs zur Optimierung
    options = [f"Flug {f['flightno']} ({f['route']}) ID {f['id']}" for f in flights_with_kpis]
    selected_option = st.selectbox("Wählen Sie einen Flug zur Bearbeitung aus", options)
    
    # ID extrahieren
    selected_id = int(selected_option.split(" ID ")[-1])
    
    # Ausgewählten Flug holen
    selected_flight = df[df["id"] == selected_id].iloc[0]
    
    # Pruefen ob dieser Flug bereits optimiert wurde
    has_simulated = agent.is_flight_optimized(selected_id)
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if not has_simulated:
            if st.button("Flug optimieren (Preissenkung und Buchungssimulation)"):
                agent.optimize_flight(selected_id)
                st.success("Die Optimierung wurde erfolgreich durchgeführt.")
                # Cache leeren damit neue Daten geladen werden
                for key in ["flights_with_kpis", "analysis_result"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        else:
            st.write("Dieser Flug wurde bereits optimiert.")
            
    with col_btn2:
        if has_simulated:
            if st.button("Optimierung zurücksetzen"):
                agent.reset_flight(selected_id)
                st.success("Die Flugdaten wurden auf den Originalzustand zurückgesetzt.")
                # Cache leeren damit neue Daten geladen werden
                for key in ["flights_with_kpis", "analysis_result"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

except Exception as e:
    st.error("Fehler beim Laden der Daten.")
    st.write("Bitte stellen Sie sicher, dass entweder die Datei flight_data.py vorhanden ist "
             "(Datenauszug) oder MySQL läuft und die Verbindungsdaten korrekt sind.")
    st.write("Fehlermeldung:")
    st.code(str(e))
