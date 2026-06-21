import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from agent import (
    FlightOptimizationAgent,
    PRICE_REDUCTION,
    TARGET_LOAD_FACTOR,
    MIN_EXTRA_PASSENGERS,
    OLLAMA_TIMEOUT,
)

from route_map import build_route_map, render_map_legend

try:
    from flight_data import get_period_presets
    HAS_PERIODS = True
except ImportError:
    HAS_PERIODS = False

CHART_COLORS = {
    "primary": "#3b82f6",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "muted": "#64748b",
    "benchmark": "#a855f7",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e2e8f0", size=12),
    margin=dict(l=20, r=30, t=50, b=20),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)


def apply_plotly_theme(fig, title):
    fig.update_layout(**PLOTLY_LAYOUT, title=dict(text=title, x=0, font=dict(size=14)))
    fig.update_xaxes(gridcolor="#334155", zerolinecolor="#334155")
    fig.update_yaxes(gridcolor="#334155", zerolinecolor="#334155")
    return fig


def build_load_factor_chart(df, weekly_avg_load):
    chart_df = df.sort_values("load_factor", ascending=True).copy()
    chart_df["belegung"] = chart_df.apply(
        lambda r: f"{int(r['passenger_count'])}/{int(r['capacity'])} Pax", axis=1
    )

    bar_colors = [
        CHART_COLORS["danger"] if lf < 30 else CHART_COLORS["warning"] if lf < 40 else CHART_COLORS["success"]
        for lf in chart_df["load_factor"]
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=chart_df["flightno"],
            x=chart_df["load_factor"],
            orientation="h",
            marker_color=bar_colors,
            text=[f"{lf:.1f} %" for lf in chart_df["load_factor"]],
            textposition="outside",
            cliponaxis=False,
            customdata=chart_df[["route", "belegung"]],
            hovertemplate=(
                "<b>Flug %{y}</b><br>"
                "Route: %{customdata[0]}<br>"
                "Belegung: %{customdata[1]}<br>"
                "Auslastung: %{x:.1f} %<extra></extra>"
            ),
        )
    )

    fig.add_vline(
        x=weekly_avg_load,
        line_dash="dash",
        line_color=CHART_COLORS["benchmark"],
        line_width=2,
    )
    fig.add_annotation(
        x=weekly_avg_load,
        y=1.08,
        yref="paper",
        text=f"Ø Zeitraum: {weekly_avg_load:.1f} %",
        showarrow=False,
        font=dict(color=CHART_COLORS["benchmark"], size=11),
    )
    fig.add_vline(x=40, line_dash="dot", line_color=CHART_COLORS["muted"], line_width=1)
    fig.add_annotation(
        x=40,
        y=1.02,
        yref="paper",
        text="Schwelle 40 %",
        showarrow=False,
        font=dict(color=CHART_COLORS["muted"], size=10),
    )

    max_x = max(chart_df["load_factor"].max(), weekly_avg_load, 45) * 1.25
    fig.update_layout(
        showlegend=False,
        xaxis_title="Auslastung in %",
        yaxis_title="",
        xaxis_range=[0, max_x],
        height=max(280, len(chart_df) * 55),
    )
    return apply_plotly_theme(fig, "Auslastung unterbelegter Flüge")


def build_revenue_chart(df):
    chart_df = df.sort_values("revenue", ascending=False)
    fig = go.Figure(
        go.Bar(
            x=chart_df["flightno"],
            y=chart_df["revenue"],
            marker_color=CHART_COLORS["primary"],
            text=[f"{r:,.0f}" for r in chart_df["revenue"]],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Umsatz: %{y:,.2f} CHF<extra></extra>",
        )
    )
    fig.update_layout(xaxis_title="Flug", yaxis_title="Umsatz CHF", showlegend=False)
    return apply_plotly_theme(fig, "Umsatz pro Flug")


def build_benchmark_chart(df, weekly_avg_load):
    categories = list(df["flightno"]) + ["Ø Zeitraum"]
    values = list(df["load_factor"]) + [weekly_avg_load]
    colors = [CHART_COLORS["danger"]] * len(df) + [CHART_COLORS["benchmark"]]

    fig = go.Figure(
        go.Bar(
            x=categories,
            y=values,
            marker_color=colors,
            text=[f"{v:.1f} %" for v in values],
            textposition="outside",
        )
    )
    fig.update_yaxes(range=[0, max(max(values) * 1.25, 55)])
    fig.update_layout(xaxis_title="", yaxis_title="Auslastung %", showlegend=False)
    return apply_plotly_theme(fig, "Vergleich mit Zeitraum-Durchschnitt")


def build_optimization_chart(original, optimized):
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Vorher",
            x=["Auslastung %", "Umsatz CHF", "Passagiere"],
            y=[original["load_factor"], original["revenue"], original["passenger_count"]],
            marker_color=CHART_COLORS["danger"],
        )
    )
    fig.add_trace(
        go.Bar(
            name="Nachher (Simulation)",
            x=["Auslastung %", "Umsatz CHF", "Passagiere"],
            y=[optimized["load_factor"], optimized["revenue"], optimized["passenger_count"]],
            marker_color=CHART_COLORS["success"],
        )
    )
    fig.update_layout(barmode="group", yaxis_title="Wert")
    return apply_plotly_theme(fig, f"Simulation: Flug {original['flightno']}")


def clear_data_cache():
    for key in ["flights_with_kpis", "analysis_result", "analysis_requested", "current_period_key"]:
        if key in st.session_state:
            del st.session_state[key]


st.set_page_config(
    page_title="Flughafen Analyseplattform",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; }
    .agent-box {
        background-color: #0f172a;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #3b82f6;
    }
    .info-banner {
        background: linear-gradient(90deg, #1e3a5f 0%, #1e293b 100%);
        padding: 16px 20px;
        border-radius: 10px;
        border-left: 4px solid #3b82f6;
        margin-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Flughafen Analyseplattform")
st.markdown(
    '<div class="info-banner">'
    "BI-Dashboard: unterbelegte Routen identifizieren, KI-Analyse, What-if-Simulation."
    "</div>",
    unsafe_allow_html=True,
)

if "agent" not in st.session_state:
    st.session_state.agent = FlightOptimizationAgent()

agent = st.session_state.agent
period_presets = get_period_presets() if HAS_PERIODS else {}

with st.sidebar:
    st.header("Filter & Steuerung")

    if period_presets:
        period_options = {
            key: f"{preset['label']}{' ⚡' if preset.get('preloaded') else ''}"
            for key, preset in period_presets.items()
        }
        selected_period = st.selectbox(
            "Beobachtungszeitraum",
            options=list(period_options.keys()),
            format_func=lambda k: period_options[k],
            index=list(period_options.keys()).index(st.session_state.get("current_period_key", "7d")),
        )

        preset = period_presets[selected_period]
        if preset.get("preloaded"):
            st.caption("⚡ Sofort geladen (vorberechneter Datenauszug)")
        elif preset.get("slow_hint"):
            st.warning(preset["slow_hint"])
            st.caption(
                "Ab 14 Tagen wird live aus MySQL geladen (54 Mio. Buchungen). "
                "Fuer schnellere Demo: `python extract_data.py` ausfuehren."
            )

        if selected_period != agent.current_period:
            agent.set_period(selected_period)
            clear_data_cache()
            st.session_state.current_period_key = selected_period

    if st.button("Daten neu laden", use_container_width=True):
        clear_data_cache()
        st.rerun()

    st.divider()
    period_info = agent.get_period_info()
    st.subheader("Datenquelle")
    st.caption(f"Zeitraum: {period_info.get('start')} – {period_info.get('end')}")
    st.caption("DB: flughafendb_large · 54 Mio. Buchungen")

    st.divider()
    ollama_ok, ollama_msg = agent.check_ollama_available()
    st.subheader("KI-Status")
    if ollama_ok:
        st.success("Ollama bereit (phi3)")
    else:
        st.warning(f"Ollama: {ollama_msg}")

try:
    period = agent.current_period
    needs_live = agent.needs_live_query(period)

    if "flights_with_kpis" not in st.session_state:
        spinner_msg = (
            "Live-Abfrage laeuft – bei grossen Zeitraeumen mehrere Minuten..."
            if needs_live
            else "Flugdaten werden geladen..."
        )
        try:
            with st.spinner(spinner_msg):
                flights = agent.fetch_flight_data(period)
                st.session_state.flights_with_kpis = agent.calculate_kpis(flights)
        except Exception as load_err:
            st.error(f"Daten fuer Zeitraum **{period_info.get('label')}** konnten nicht geladen werden.")
            if needs_live:
                st.info(
                    "Fuer Zeitraeume ab 14 Tagen ist eine MySQL-Verbindung noetig "
                    "oder ein vorberechneter Extrakt via `python extract_data.py`."
                )
            st.code(str(load_err))
            st.stop()

    flights_with_kpis = st.session_state.flights_with_kpis

    if not flights_with_kpis:
        st.warning(
            f"Keine unterbelegten Flüge (< 40 % Auslastung) im Zeitraum "
            f"**{period_info.get('label')}** gefunden. Bitte anderen Zeitraum wählen."
        )
        st.stop()

    df = pd.DataFrame(flights_with_kpis)
    context = agent.fetch_route_context(period)
    weekly_stats = context.get("weekly_stats", {})
    weekly_avg_load = float(weekly_stats.get("avg_load_factor") or 0)

    tab_map, tab_overview, tab_analysis, tab_action = st.tabs(
        ["Weltkarte", "Übersicht", "KI-Analyse", "Optimierung"]
    )

    map_flights = agent.enrich_flights_geography([dict(f) for f in flights_with_kpis])
    top_flights_raw = context.get("best_flights", [])[:5]
    top_map_flights = agent.enrich_flights_geography([dict(f) for f in top_flights_raw])

    with tab_map:
        st.subheader("Globale Routenanalyse")
        st.caption(
            "Rot/orange/gelb: unterbelegte Routen (< 40 %). "
            "Grün gestrichelt: Top 5 bestausgelastete Flüge im Zeitraum."
        )

        st.markdown(render_map_legend(), unsafe_allow_html=True)
        route_fig, routes_on_map, top_on_map = build_route_map(map_flights, top_map_flights)
        st.plotly_chart(route_fig, use_container_width=True)

        if routes_on_map == 0 and top_on_map == 0:
            st.warning(
                "Koordinaten fehlen im Datensatz. Entweder MySQL mit `airport_geo` starten "
                "oder `python extract_data.py` erneut ausfuehren (liefert Geo-Daten mit)."
            )
        else:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Unterbelegte Routen", routes_on_map)
            m2.metric("Top-Routen", top_on_map)
            m3.metric("Niedrigste Auslastung", f"{df['load_factor'].min():.1f} %")
            if top_map_flights:
                top_load = max(float(f.get("load_factor", 0)) for f in top_map_flights)
                m4.metric("Höchste Auslastung (Top)", f"{top_load:.1f} %")
            else:
                m4.metric("Route mit meiste Pax", df.loc[df["passenger_count"].idxmax(), "flightno"])

            with st.expander("Routen-Details"):
                if map_flights:
                    st.markdown("**Unterbelegte Flüge**")
                    map_df = pd.DataFrame(map_flights)
                    cols = [c for c in [
                        "flightno", "route", "dep_country", "arr_country",
                        "load_factor", "passenger_count", "revenue",
                    ] if c in map_df.columns]
                    st.dataframe(map_df[cols], use_container_width=True, hide_index=True)
                if top_map_flights:
                    st.markdown("**Top 5 Auslastung**")
                    top_df = pd.DataFrame(top_map_flights)
                    top_cols = [c for c in [
                        "flightno", "route", "dep_country", "arr_country",
                        "load_factor", "passenger_count",
                    ] if c in top_df.columns]
                    st.dataframe(top_df[top_cols], use_container_width=True, hide_index=True)

    with tab_overview:
        col1, col2, col3, col4 = st.columns(4)
        avg_load = df["load_factor"].mean()
        total_rev = df["revenue"].sum()
        total_passengers = df["passenger_count"].sum()
        optimized_count = sum(1 for f in flights_with_kpis if agent.is_flight_optimized(f["id"]))

        col1.metric("Ø Auslastung", f"{avg_load:.1f} %", delta=f"{avg_load - weekly_avg_load:.1f} % vs. Zeitraum", delta_color="inverse")
        col2.metric("Gesamtumsatz", f"{total_rev:,.0f} CHF")
        col3.metric("Passagiere", int(total_passengers))
        col4.metric("Optimiert", optimized_count)

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(build_load_factor_chart(df, weekly_avg_load), use_container_width=True)
        with c2:
            st.plotly_chart(build_revenue_chart(df), use_container_width=True)

        st.plotly_chart(build_benchmark_chart(df, weekly_avg_load), use_container_width=True)

        st.subheader(f"Unterbelegte Flüge – {period_info.get('label', '')}")
        st.dataframe(
            df.rename(columns={
                "flightno": "Flugnummer", "route": "Route", "departure_time": "Abflug",
                "capacity": "Kapazität", "passenger_count": "Passagiere",
                "ticket_price": "Ø Preis CHF", "load_factor": "Auslastung %", "revenue": "Umsatz CHF",
            }),
            use_container_width=True,
            hide_index=True,
        )

    with tab_analysis:
        st.subheader("KI-gestützte Analyse")
        st.caption(f"Ollama phi3 · Timeout {OLLAMA_TIMEOUT // 60} Min. · Erste Analyse kann 1–2 Min. dauern.")

        if st.button("Analyse starten", type="primary"):
            st.session_state.analysis_requested = True
            if "analysis_result" in st.session_state:
                del st.session_state["analysis_result"]

        if st.session_state.get("analysis_requested"):
            if "analysis_result" not in st.session_state:
                with st.spinner("KI-Analyse läuft… bitte warten"):
                    st.session_state.analysis_result = agent.generate_analysis(flights_with_kpis)

            if agent.last_analysis_source == "llm":
                st.success("LLM-gestützte Analyse (Ollama phi3)")
            else:
                st.info("Regelbasierter Fallback")
                if agent.last_llm_error:
                    st.caption(f"Grund: {agent.last_llm_error}")

            st.markdown('<div class="agent-box">', unsafe_allow_html=True)
            st.markdown(st.session_state.analysis_result.replace("\n", "\n\n"))
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("«Analyse starten» klicken – blockiert nicht beim Seitenaufbau.")

    with tab_action:
        st.subheader("What-if-Simulation")
        st.markdown(
            f"**Modell:** Durchschnittspreis **−{PRICE_REDUCTION * 100:.0f} %**, "
            f"simulierte Nachfrage bis **{TARGET_LOAD_FACTOR * 100:.0f} %** Auslastung "
            f"(mind. **+{MIN_EXTRA_PASSENGERS}** Passagiere). Keine echten DB-Schreibungen im Demo-Modus."
        )

        options = [f"{f['flightno']} – {f['route']}" for f in flights_with_kpis]
        selected_idx = st.selectbox("Flug auswählen", range(len(options)), format_func=lambda i: options[i])
        selected_id = flights_with_kpis[selected_idx]["id"]
        has_simulated = agent.is_flight_optimized(selected_id)
        details = agent.get_optimization_details(selected_id)

        with st.expander("Wie wird die Simulation berechnet?", expanded=not has_simulated):
            if details:
                st.markdown(
                    f"| Parameter | Wert |\n|---|---|\n"
                    f"| Ziel-Auslastung | {details['target_load_pct']:.0f} % |\n"
                    f"| Preissenkung | {details['price_reduction_pct']:.0f} % |\n"
                    f"| Min. zusätzliche Pax | {MIN_EXTRA_PASSENGERS} |"
                )
                st.markdown("**Rechenschritte (Vorschau):**")
                for step in details["steps"]:
                    st.markdown(f"- {step}")
                st.markdown(
                    f"**Umsatz:** {details['formula_revenue_before']} = "
                    f"**{details['revenue_before']:,.2f} CHF** → "
                    f"{details['formula_revenue_after']} = "
                    f"**{details['revenue_after']:,.2f} CHF** "
                    f"({'+' if details['revenue_delta'] >= 0 else ''}{details['revenue_delta']:,.2f} CHF)"
                )

        c1, c2 = st.columns(2)
        with c1:
            if not has_simulated and st.button("Simulation starten", type="primary", use_container_width=True):
                agent.optimize_flight(selected_id)
                clear_data_cache()
                st.rerun()
        with c2:
            if has_simulated and st.button("Zurücksetzen", use_container_width=True):
                agent.reset_flight(selected_id)
                clear_data_cache()
                st.rerun()

        if has_simulated and details:
            optimized_flight = next(f for f in agent.calculate_kpis(agent.fetch_flight_data()) if f["id"] == selected_id)
            original_kpi = agent.calculate_kpis([agent.get_baseline_flight(selected_id)])[0]

            st.plotly_chart(build_optimization_chart(original_kpi, optimized_flight), use_container_width=True)

            d1, d2, d3 = st.columns(3)
            d1.metric("Auslastung", f"{optimized_flight['load_factor']:.1f} %", delta=f"{optimized_flight['load_factor'] - original_kpi['load_factor']:.1f} %")
            d2.metric("Umsatz", f"{optimized_flight['revenue']:,.0f} CHF", delta=f"{optimized_flight['revenue'] - original_kpi['revenue']:,.0f} CHF")
            d3.metric("Passagiere", optimized_flight["passenger_count"], delta=optimized_flight["passenger_count"] - original_kpi["passenger_count"])

            st.markdown("**Angewendete Massnahmen:**")
            for step in details["steps"]:
                st.markdown(f"- {step}")

except Exception as e:
    st.error("Fehler beim Laden der Daten.")
    st.code(str(e))
