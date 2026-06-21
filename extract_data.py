"""Einmaliger Datenauszug aus der Datenbank.
Extrahiert Flugdaten fuer mehrere Zeitraeume und speichert sie als Python-Modul.
"""
import json
from datetime import datetime, timedelta

import mysql.connector

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Startup.6"
DB_NAME = "flughafendb_large"

PERIOD_DEFINITIONS = [
    ("1d", "1 Tag (1. Juni)", "2015-06-01", "2015-06-01", True),
    ("3d", "3 Tage (1.–3. Juni)", "2015-06-01", "2015-06-03", True),
    ("7d", "1 Woche (1.–7. Juni)", "2015-06-01", "2015-06-07", True),
    ("14d", "2 Wochen (1.–14. Juni)", "2015-06-01", "2015-06-14", False),
    ("30d", "1 Monat (Juni 2015)", "2015-06-01", "2015-06-30", False),
]

UNDERPERFORMING_QUERY = """
    SELECT f.flight_id as id,
           f.flightno,
           CONCAT(dep.name, ' nach ', arr.name) as route,
           f.departure as departure_time,
           ap.capacity,
           COUNT(b.booking_id) as passenger_count,
           COALESCE(AVG(b.price), 0.0) as ticket_price
    FROM flight f
    JOIN airport dep ON f.`from` = dep.airport_id
    JOIN airport arr ON f.`to` = arr.airport_id
    JOIN airplane ap ON f.airplane_id = ap.airplane_id
    LEFT JOIN booking b ON b.flight_id = f.flight_id
    WHERE f.departure BETWEEN %s AND %s
    GROUP BY f.flight_id, f.flightno, dep.name, arr.name, f.departure, ap.capacity
    HAVING COUNT(b.booking_id) > 0 AND COUNT(b.booking_id) < ap.capacity * 0.40
    ORDER BY passenger_count ASC
    LIMIT 15
"""

BEST_QUERY = """
    SELECT f.flight_id as id,
           f.flightno,
           CONCAT(dep.name, ' nach ', arr.name) as route,
           f.departure as departure_time,
           ap.capacity,
           COUNT(b.booking_id) as passenger_count,
           ROUND(COUNT(b.booking_id) / ap.capacity * 100, 1) as load_factor,
           COALESCE(AVG(b.price), 0.0) as avg_price
    FROM flight f
    JOIN airport dep ON f.`from` = dep.airport_id
    JOIN airport arr ON f.`to` = arr.airport_id
    JOIN airplane ap ON f.airplane_id = ap.airplane_id
    LEFT JOIN booking b ON b.flight_id = f.flight_id
    WHERE f.departure BETWEEN %s AND %s
    GROUP BY f.flight_id, f.flightno, dep.name, arr.name, f.departure, ap.capacity
    HAVING COUNT(b.booking_id) > 0
    ORDER BY load_factor DESC
    LIMIT 10
"""

STATS_QUERY = """
    SELECT COUNT(DISTINCT f.flight_id) as total_flights,
           SUM(sub.pax) as total_passengers,
           AVG(sub.pax) as avg_passengers_per_flight,
           AVG(sub.load_pct) as avg_load_factor
    FROM flight f
    JOIN (
        SELECT b.flight_id, COUNT(*) as pax,
               COUNT(*) * 100.0 / ap2.capacity as load_pct
        FROM booking b
        JOIN flight f2 ON b.flight_id = f2.flight_id
        JOIN airplane ap2 ON f2.airplane_id = ap2.airplane_id
        WHERE f2.departure BETWEEN %s AND %s
        GROUP BY b.flight_id, ap2.capacity
    ) sub ON f.flight_id = sub.flight_id
    WHERE f.departure BETWEEN %s AND %s
"""


def normalize_flights(flights):
    for f in flights:
        if isinstance(f.get("departure_time"), datetime):
            f["departure_time"] = f["departure_time"].strftime("%Y-%m-%d %H:%M:%S")
        if "ticket_price" in f:
            f["ticket_price"] = float(f["ticket_price"])
        if "avg_price" in f:
            f["avg_price"] = float(f["avg_price"])
        if "load_factor" in f:
            f["load_factor"] = float(f["load_factor"])
    return flights


def extract_period(cursor, start_date, end_date):
    start_ts = f"{start_date} 00:00:00"
    end_ts = f"{end_date} 23:59:59"

    cursor.execute(UNDERPERFORMING_QUERY, (start_ts, end_ts))
    under = normalize_flights(cursor.fetchall())

    cursor.execute(BEST_QUERY, (start_ts, end_ts))
    best = normalize_flights(cursor.fetchall())

    cursor.execute(STATS_QUERY, (start_ts, end_ts, start_ts, end_ts))
    stats = cursor.fetchone() or {}
    for key, val in stats.items():
        if val is not None and key != "total_flights":
            stats[key] = float(val)

    return {"underperforming": under, "best": best, "stats": stats}


def main():
    print("Verbinde mit Datenbank...")
    conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    cursor = conn.cursor(dictionary=True)

    preloaded = {}
    extended = {}
    presets = {}

    for key, label, start, end, is_preloaded in PERIOD_DEFINITIONS:
        print(f"\nExtrahiere Zeitraum {label} ({start} bis {end})...")
        data = extract_period(cursor, start, end)
        print(f"  {len(data['underperforming'])} unterbelegte, {len(data['best'])} Top-Fluege")

        presets[key] = {
            "label": label,
            "start": start,
            "end": end,
            "preloaded": is_preloaded or key in ("14d", "30d"),
            "slow_hint": None if is_preloaded or key in ("14d", "30d") else "Live-Abfrage noetig",
        }

        if is_preloaded:
            preloaded[key] = data
        else:
            extended[key] = data
            presets[key]["preloaded"] = True
            presets[key]["slow_hint"] = None

    cursor.close()
    conn.close()

    # Legacy-Daten fuer Abwaertskompatibilitaet (7-Tage-Default)
    week = preloaded.get("7d") or extended.get("7d", {})
    underperforming = week.get("underperforming", [])
    best_performers = week.get("best", [])
    weekly_stats = week.get("stats", {})

    output = f'''"""
Vorberechneter Datenauszug aus der Datenbank flughafendb_large.
Extrahiert am: {datetime.now().strftime("%Y-%m-%d %H:%M")}

Datenbank-Groesse: 462'553 Fluege, 54'304'619 Buchungen
Zeitraeume: 1d, 3d, 7d (sofort) + 14d, 30d (vorberechnet via extract_data.py)
"""

UNDERPERFORMING_FLIGHTS = {json.dumps(underperforming, indent=4, ensure_ascii=False, default=str)}

BEST_PERFORMING_FLIGHTS = {json.dumps(best_performers, indent=4, ensure_ascii=False, default=str)}

WEEKLY_STATS = {json.dumps(weekly_stats, indent=4, ensure_ascii=False, default=str)}

PERIOD_PRESETS = {json.dumps(presets, indent=4, ensure_ascii=False, default=str)}

PRELOADED_PERIOD_DATA = {json.dumps(preloaded, indent=4, ensure_ascii=False, default=str)}

EXTENDED_PERIOD_DATA = {json.dumps(extended, indent=4, ensure_ascii=False, default=str)}


def get_underperforming_flights(limit=5):
    return UNDERPERFORMING_FLIGHTS[:limit]


def get_best_performing_flights(limit=5):
    return BEST_PERFORMING_FLIGHTS[:limit]


def get_weekly_stats():
    return WEEKLY_STATS


def get_period_presets():
    return PERIOD_PRESETS


def is_period_preloaded(period_key):
    preset = PERIOD_PRESETS.get(period_key, {{}})
    if preset.get("preloaded"):
        return True
    return period_key in EXTENDED_PERIOD_DATA


def get_period_data(period_key):
    if period_key in EXTENDED_PERIOD_DATA:
        return EXTENDED_PERIOD_DATA[period_key]
    return PRELOADED_PERIOD_DATA.get(period_key)
'''

    with open("flight_data.py", "w", encoding="utf-8") as f:
        f.write(output)

    print("\nflight_data.py erfolgreich erstellt!")


if __name__ == "__main__":
    main()
