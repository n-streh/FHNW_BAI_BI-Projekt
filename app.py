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

# Agent initialisieren
agent = FlightOptimizationAgent()

try:
    flights = agent.fetch_flight_data()
    flights_with_kpis = agent.calculate_kpis(flights)
    
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

    # Agenten-Analyse anfordern
    st.subheader("Analyse und Denkprozess des Agenten")
    
    analysis_result = agent.generate_analysis(flights_with_kpis)
    
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
    
    # Überprüfen ob dieser Flug bereits simulierte Buchungen hat
    # Wenn ID >= 10000000 existiert, ist er optimiert
    conn = agent.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM booking WHERE booking_id >= 10000000 AND flight_id = %s",
        (selected_id,)
    )
    has_simulated = cursor.fetchone()[0] > 0
    cursor.close()
    conn.close()
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if not has_simulated:
            if st.button("Flug optimieren (Preissenkung und Buchungssimulation)"):
                agent.optimize_flight(selected_id)
                st.success("Die Optimierung wurde erfolgreich durchgeführt.")
                st.rerun()
        else:
            st.write("Dieser Flug wurde bereits optimiert.")
            
    with col_btn2:
        if has_simulated:
            if st.button("Optimierung zurücksetzen"):
                agent.reset_flight(selected_id)
                st.success("Die Flugdaten wurden auf den Originalzustand zurückgesetzt.")
                st.rerun()

except Exception as e:
    st.error("Verbindung zur MySQL Datenbank fehlgeschlagen.")
    st.write("Bitte stellen Sie sicher, dass MySQL läuft und die Verbindungsdaten in db_setup.py und agent.py korrekt eingetragen sind.")
    st.write("Fehlermeldung:")
    st.code(str(e))
