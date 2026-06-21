"""Weltkarte fuer unterbelegte und top-ausgelastete Flugrouten (Plotly Scattergeo)."""
import math

import plotly.graph_objects as go

COLORS = {
    "critical": "#ef4444",
    "warning": "#f97316",
    "moderate": "#fbbf24",
    "top": "#22c55e",
    "top_glow": "rgba(34, 197, 94, 0.2)",
    "airport": "#38bdf8",
    "land": "#334155",
    "ocean": "#0f172a",
    "grid": "#1e293b",
    "country": "#475569",
}


def _has_geo(flight):
    keys = ("dep_lat", "dep_lon", "arr_lat", "arr_lon")
    return all(flight.get(k) is not None for k in keys)


def _load_color(load_factor):
    if load_factor < 25:
        return COLORS["critical"]
    if load_factor < 32:
        return COLORS["warning"]
    return COLORS["moderate"]


def normalize_flight_for_map(flight):
    """Vereinheitlicht Felder zwischen Unterbelegt- und Top-Flug Datensaetzen."""
    f = dict(flight)
    if "ticket_price" not in f and "avg_price" in f:
        f["ticket_price"] = f["avg_price"]
    if "revenue" not in f and f.get("ticket_price") is not None:
        f["revenue"] = f["passenger_count"] * float(f["ticket_price"])
    if "load_factor" not in f and f.get("capacity"):
        f["load_factor"] = round(f["passenger_count"] / f["capacity"] * 100, 2)
    return f


def _arc_points(lat1, lon1, lat2, lon2, n=30):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    points = []
    for i in range(n + 1):
        f = i / n
        d = math.acos(
            min(
                1.0,
                max(
                    -1.0,
                    math.sin(lat1) * math.sin(lat2)
                    + math.cos(lat1) * math.cos(lat2) * math.cos(lon2 - lon1),
                ),
            )
        )
        if d == 0:
            points.append((math.degrees(lat1), math.degrees(lon1)))
            continue
        a = math.sin((1 - f) * d) / math.sin(d)
        b = math.sin(f * d) / math.sin(d)
        x = a * math.cos(lat1) * math.cos(lon1) + b * math.cos(lat2) * math.cos(lon2)
        y = a * math.cos(lat1) * math.sin(lon1) + b * math.cos(lat2) * math.sin(lon2)
        z = a * math.sin(lat1) + b * math.sin(lat2)
        lat = math.degrees(math.atan2(z, math.sqrt(x * x + y * y)))
        lon = math.degrees(math.atan2(y, x))
        points.append((lat, lon))
    return points


def _route_hover(flight, label):
    dep = flight.get("dep_name") or flight["route"].split(" nach ")[0]
    arr = flight.get("arr_name") or flight["route"].split(" nach ")[-1]
    load = float(flight["load_factor"])
    return (
        f"<b>{flight['flightno']}</b> ({label})<br>"
        f"{dep} → {arr}<br>"
        f"Auslastung: {load:.1f} %<br>"
        f"Passagiere: {flight['passenger_count']}/{flight['capacity']}<br>"
        f"Umsatz: {flight.get('revenue', 0):,.0f} CHF"
    )


def _add_route(fig, flight, *, route_type, all_lats, all_lons):
    dep_lat = float(flight["dep_lat"])
    dep_lon = float(flight["dep_lon"])
    arr_lat = float(flight["arr_lat"])
    arr_lon = float(flight["arr_lon"])
    load = float(flight["load_factor"])

    arc = _arc_points(dep_lat, dep_lon, arr_lat, arr_lon)
    arc_lats = [p[0] for p in arc]
    arc_lons = [p[1] for p in arc]
    all_lats.extend(arc_lats)
    all_lons.extend(arc_lons)

    if route_type == "top":
        color = COLORS["top"]
        width = 2.5
        dash = "dash"
        glow_width = width + 8
        glow_opacity = 0.18
        label = "Top-Auslastung"
    else:
        color = _load_color(load)
        width = 1.5 + (40 - min(load, 40)) / 8
        dash = "solid"
        glow_width = width + 6
        glow_opacity = 0.12
        label = "Unterbelegt"

    hover = _route_hover(flight, label)

    fig.add_trace(
        go.Scattergeo(
            lon=arc_lons,
            lat=arc_lats,
            mode="lines",
            line=dict(width=glow_width, color=color),
            opacity=glow_opacity,
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scattergeo(
            lon=arc_lons,
            lat=arc_lats,
            mode="lines",
            line=dict(width=width, color=color, dash=dash),
            opacity=0.92,
            name=flight["flightno"],
            hovertemplate=hover + "<extra></extra>",
            showlegend=False,
        )
    )


def _collect_airports(flights, airport_points):
    for flight in flights:
        for prefix in ("dep", "arr"):
            name = flight.get(f"{prefix}_name") or ""
            lat = flight.get(f"{prefix}_lat")
            lon = flight.get(f"{prefix}_lon")
            if lat is None or lon is None:
                continue
            key = (round(float(lat), 2), round(float(lon), 2))
            airport_points[key] = {
                "name": name,
                "lat": float(lat),
                "lon": float(lon),
            }


def build_route_map(underperforming_flights, top_flights=None):
    """Erstellt interaktive Weltkarte mit Problem- und Top-Routen."""
    bad_flights = [normalize_flight_for_map(f) for f in underperforming_flights if _has_geo(f)]
    good_flights = [normalize_flight_for_map(f) for f in (top_flights or []) if _has_geo(f)]

    fig = go.Figure()
    if not bad_flights and not good_flights:
        fig.update_layout(
            title="Keine Koordinaten verfuegbar",
            paper_bgcolor="rgba(0,0,0,0)",
            height=500,
        )
        return fig, 0, 0

    all_lats, all_lons = [], []
    airport_points = {}

    for flight in sorted(good_flights, key=lambda f: f["load_factor"]):
        _add_route(fig, flight, route_type="top", all_lats=all_lats, all_lons=all_lons)

    for flight in sorted(bad_flights, key=lambda f: f["load_factor"], reverse=True):
        _add_route(fig, flight, route_type="bad", all_lats=all_lats, all_lons=all_lons)

    _collect_airports(bad_flights + good_flights, airport_points)

    if airport_points:
        fig.add_trace(
            go.Scattergeo(
                lon=[p["lon"] for p in airport_points.values()],
                lat=[p["lat"] for p in airport_points.values()],
                mode="markers",
                marker=dict(size=7, color=COLORS["airport"], line=dict(width=1, color="#e2e8f0")),
                text=[p["name"] for p in airport_points.values()],
                hovertemplate="<b>%{text}</b><br>%{lat:.2f}, %{lon:.2f}<extra></extra>",
                name="Flughafen",
                showlegend=False,
            )
        )

    center_lat = sum(all_lats) / len(all_lats) if all_lats else 0
    center_lon = sum(all_lons) / len(all_lons) if all_lons else 0

    fig.update_geos(
        projection_type="natural earth",
        projection=dict(rotation=dict(lon=center_lon, lat=center_lat, roll=0)),
        bgcolor="rgba(0,0,0,0)",
        showland=True,
        landcolor=COLORS["land"],
        showcountries=True,
        countrycolor=COLORS["country"],
        showocean=True,
        oceancolor=COLORS["ocean"],
        showlakes=True,
        lakecolor=COLORS["ocean"],
        coastlinewidth=0.6,
        lataxis=dict(showgrid=True, gridcolor=COLORS["grid"], gridwidth=0.4),
        lonaxis=dict(showgrid=True, gridcolor=COLORS["grid"], gridwidth=0.4),
    )

    fig.update_layout(
        title=dict(
            text="Flugrouten weltweit – Unterbelegt vs. Top-Auslastung",
            x=0.5,
            xanchor="center",
            font=dict(size=16, color="#e2e8f0"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        height=620,
        margin=dict(l=0, r=0, t=60, b=20),
    )

    return fig, len(bad_flights), len(good_flights)


def render_map_legend():
    """Streamlit-Hilfsmarkup fuer die Kartenlegende (nicht in Plotly – vermeidet Abschneiden)."""
    return """
    <div style="
        display:flex; flex-wrap:wrap; gap:20px; justify-content:center;
        padding:10px 16px; margin-bottom:8px;
        background:#1e293b; border-radius:8px; border:1px solid #334155;
        font-size:14px; color:#e2e8f0;
    ">
        <span><span style="color:#ef4444;font-size:18px;">●</span> Unterbelegt &lt;25&nbsp;%</span>
        <span><span style="color:#f97316;font-size:18px;">●</span> 25–32&nbsp;%</span>
        <span><span style="color:#fbbf24;font-size:18px;">●</span> 32–40&nbsp;%</span>
        <span><span style="color:#22c55e;font-size:18px;">- -</span> Top&nbsp;5 Auslastung</span>
        <span><span style="color:#38bdf8;font-size:18px;">●</span> Flughafen</span>
    </div>
    """
