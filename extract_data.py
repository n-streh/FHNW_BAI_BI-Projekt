"""Einmaliger Datenauszug aus der Datenbank.

Strategie: Eine Hauptabfrage fuer den maximalen Zeitraum (Juni 2015),
danach werden alle kuerzeren Perioden per Python-Filter abgeleitet.
"""
import json
import sys
import time
from datetime import datetime

import mysql.connector

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Startup.6"
DB_NAME = "flughafendb_large"

MASTER_START = "2015-06-01"
MASTER_END = "2015-06-30"

PERIOD_DEFINITIONS = [
    ("1d", "1 Tag (1. Juni)", "2015-06-01", "2015-06-01"),
    ("3d", "3 Tage (1.–3. Juni)", "2015-06-01", "2015-06-03"),
    ("7d", "1 Woche (1.–7. Juni)", "2015-06-01", "2015-06-07"),
    ("14d", "2 Wochen (1.–14. Juni)", "2015-06-01", "2015-06-14"),
    ("30d", "1 Monat (Juni 2015)", "2015-06-01", "2015-06-30"),
]

MASTER_QUERY = """
    SELECT f.flight_id as id,
           f.flightno,
           CONCAT(dep.name, ' nach ', arr.name) as route,
           dep.name as dep_name,
           arr.name as arr_name,
           MAX(dep_geo.latitude) as dep_lat,
           MAX(dep_geo.longitude) as dep_lon,
           MAX(dep_geo.country) as dep_country,
           MAX(arr_geo.latitude) as arr_lat,
           MAX(arr_geo.longitude) as arr_lon,
           MAX(arr_geo.country) as arr_country,
           f.departure as departure_time,
           ap.capacity,
           COUNT(b.booking_id) as passenger_count,
           COALESCE(AVG(b.price), 0.0) as ticket_price,
           ROUND(COUNT(b.booking_id) / ap.capacity * 100, 2) as load_factor
    FROM flight f
    JOIN airport dep ON f.`from` = dep.airport_id
    JOIN airport arr ON f.`to` = arr.airport_id
    LEFT JOIN airport_geo dep_geo ON dep.airport_id = dep_geo.airport_id
    LEFT JOIN airport_geo arr_geo ON arr.airport_id = arr_geo.airport_id
    JOIN airplane ap ON f.airplane_id = ap.airplane_id
    INNER JOIN booking b ON b.flight_id = f.flight_id
    WHERE f.departure BETWEEN %s AND %s
    GROUP BY f.flight_id, f.flightno, dep.name, arr.name, f.departure, ap.capacity
"""


class ProgressBar:
    def __init__(self, total, label="", width=40):
        self.total = max(total, 1)
        self.current = 0
        self.label = label
        self.width = width
        self._start = time.time()

    def update(self, step=1, detail=""):
        self.current = min(self.current + step, self.total)
        pct = self.current / self.total
        filled = int(self.width * pct)
        bar = "#" * filled + "-" * (self.width - filled)
        suffix = f" | {detail}" if detail else ""
        line = f"\r{self.label} [{bar}] {self.current}/{self.total} ({pct * 100:5.1f}%){suffix}"
        sys.stdout.write(line)
        sys.stdout.flush()

    def finish(self, message=""):
        self.current = self.total
        self.update(0)
        if message:
            sys.stdout.write(f"\n{message}\n")
        else:
            sys.stdout.write("\n")
        sys.stdout.flush()


def normalize_flight(row):
    if isinstance(row.get("departure_time"), datetime):
        row["departure_time"] = row["departure_time"].strftime("%Y-%m-%d %H:%M:%S")
    row["departure_date"] = row["departure_time"][:10]
    row["passenger_count"] = int(row["passenger_count"])
    row["capacity"] = int(row["capacity"])
    row["ticket_price"] = float(row["ticket_price"])
    row["load_factor"] = float(row["load_factor"])
    for key in ("dep_lat", "dep_lon", "arr_lat", "arr_lon"):
        if row.get(key) is not None:
            row[key] = float(row[key])
    return row


def filter_by_date(flights, start, end):
    return [f for f in flights if start <= f["departure_date"] <= end]


def build_period_stats(flights):
    if not flights:
        return {
            "total_flights": 0,
            "total_passengers": 0.0,
            "avg_passengers_per_flight": 0.0,
            "avg_load_factor": 0.0,
        }
    total_pax = sum(f["passenger_count"] for f in flights)
    return {
        "total_flights": len(flights),
        "total_passengers": float(total_pax),
        "avg_passengers_per_flight": round(total_pax / len(flights), 4),
        "avg_load_factor": round(sum(f["load_factor"] for f in flights) / len(flights), 6),
    }


def build_period_data(all_flights, start, end):
    in_range = filter_by_date(all_flights, start, end)

    underperforming = sorted(
        [f for f in in_range if f["load_factor"] < 40.0],
        key=lambda f: f["passenger_count"],
    )[:15]

    best = sorted(in_range, key=lambda f: f["load_factor"], reverse=True)[:10]
    best_export = [
        {k: v for k, v in f.items() if k not in ("departure_date",)}
        for f in best
    ]

    under_export = [
        {k: v for k, v in f.items() if k not in ("departure_date", "load_factor")}
        for f in underperforming
    ]

    return {
        "underperforming": under_export,
        "best": best_export,
        "stats": build_period_stats(in_range),
    }


def fetch_master_flights(cursor, start_date, end_date):
    start_ts = f"{start_date} 00:00:00"
    end_ts = f"{end_date} 23:59:59"

    print(f"Hauptabfrage: {start_date} bis {end_date} (einmalig fuer alle Zeitraeume)")
    print("Dies kann bei 54 Mio. Buchungen mehrere Minuten dauern...\n")

    query_start = time.time()
    cursor.execute(MASTER_QUERY, (start_ts, end_ts))

    rows = []
    batch_size = 5000
    while True:
        batch = cursor.fetchmany(batch_size)
        if not batch:
            break
        rows.extend(normalize_flight(r) for r in batch)
        sys.stdout.write(f"\r  DB-Laden    {len(rows):,} Fluege geladen...")
        sys.stdout.flush()

    elapsed = time.time() - query_start
    print(f"\r  DB-Laden    {len(rows):,} Fluege geladen in {elapsed:.1f}s\n")
    return rows


def to_python_literal(obj, indent=4):
    text = json.dumps(obj, indent=indent, ensure_ascii=False, default=str)
    return (
        text.replace(": true", ": True")
        .replace(": false", ": False")
        .replace(": null", ": None")
    )


def write_flight_data(preloaded, presets):
    week = preloaded.get("7d", {})
    underperforming = week.get("underperforming", [])
    best_performers = week.get("best", [])
    weekly_stats = week.get("stats", {})

    output = f'''"""
Vorberechneter Datenauszug aus der Datenbank flughafendb_large.
Extrahiert am: {datetime.now().strftime("%Y-%m-%d %H:%M")}

Datenbank-Groesse: 462'553 Fluege, 54'304'619 Buchungen
Extraktion: 1 Hauptabfrage (Juni), Zeitraeume per Filter abgeleitet
"""

UNDERPERFORMING_FLIGHTS = {to_python_literal(underperforming, indent=4)}

BEST_PERFORMING_FLIGHTS = {to_python_literal(best_performers, indent=4)}

WEEKLY_STATS = {to_python_literal(weekly_stats, indent=4)}

PERIOD_PRESETS = {to_python_literal(presets, indent=4)}

PRELOADED_PERIOD_DATA = {to_python_literal(preloaded, indent=4)}

EXTENDED_PERIOD_DATA = {{}}


def get_underperforming_flights(limit=5):
    return UNDERPERFORMING_FLIGHTS[:limit]


def get_best_performing_flights(limit=5):
    return BEST_PERFORMING_FLIGHTS[:limit]


def get_weekly_stats():
    return WEEKLY_STATS


def get_period_presets():
    return PERIOD_PRESETS


def is_period_preloaded(period_key):
    return period_key in PRELOADED_PERIOD_DATA or period_key in EXTENDED_PERIOD_DATA


def get_period_data(period_key):
    if period_key in EXTENDED_PERIOD_DATA:
        return EXTENDED_PERIOD_DATA[period_key]
    return PRELOADED_PERIOD_DATA.get(period_key)
'''

    write_progress = ProgressBar(1, label="Datei     ")
    write_progress.update(1, detail="flight_data.py")
    with open("flight_data.py", "w", encoding="utf-8") as f:
        f.write(output)
    write_progress.finish()


def main():
    overall = ProgressBar(3, label="Gesamt   ")

    print("=" * 60)
    print("FHNW BI-Projekt – Datenauszug (optimiert)")
    print("=" * 60)

    print("\n[1/3] Verbinde mit Datenbank...")
    conn = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME,
    )
    cursor = conn.cursor(dictionary=True)
    overall.update(1, "Verbunden")
    print(f"  Verbunden mit '{DB_NAME}'")

    print("\n[2/3] Hauptabfrage ausfuehren...")
    all_flights = fetch_master_flights(cursor, MASTER_START, MASTER_END)
    cursor.close()
    conn.close()
    overall.update(1, f"{len(all_flights):,} Fluege")

    print("\n[3/3] Zeitraeume aus Hauptdaten ableiten...")
    preloaded = {}
    presets = {}
    period_progress = ProgressBar(len(PERIOD_DEFINITIONS), label="Perioden ")

    for key, label, start, end in PERIOD_DEFINITIONS:
        data = build_period_data(all_flights, start, end)
        preloaded[key] = data
        presets[key] = {
            "label": label,
            "start": start,
            "end": end,
            "preloaded": True,
            "slow_hint": None,
        }
        period_progress.update(
            1,
            detail=f"{label}: {len(data['underperforming'])} unterbelegt",
        )

    period_progress.finish()
    overall.update(1, "Fertig")
    overall.finish()

    write_flight_data(preloaded, presets)

    print("\n" + "=" * 60)
    print("Zusammenfassung:")
    for key, label, start, end in PERIOD_DEFINITIONS:
        d = preloaded[key]
        print(
            f"  {label:28} {len(d['underperforming']):2} unterbelegt | "
            f"{d['stats']['total_flights']:,} Fluege | "
            f"Ø {d['stats']['avg_load_factor']:.1f} %"
        )
    print("=" * 60)
    print("Fertig.\n")


if __name__ == "__main__":
    main()
