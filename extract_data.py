"""Einmaliger Datenauszug aus der Datenbank.
Extrahiert Flugdaten mit aggregierten Buchungsdaten und speichert sie als Python-Modul.
"""
import mysql.connector
import json
from datetime import datetime

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Startup.6"
DB_NAME = "flughafendb_large"

conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
cursor = conn.cursor(dictionary=True)

print("Extrahiere unterbelegte Fluege (erste Juniwoche 2015)...")
print("Dies kann einige Minuten dauern bei 54 Mio Buchungen...")

# Hauptquery: Unterbelegte Fluege
query = """
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
    WHERE f.departure BETWEEN '2015-06-01 00:00:00' AND '2015-06-07 23:59:59'
    GROUP BY f.flight_id, f.flightno, dep.name, arr.name, f.departure, ap.capacity
    HAVING COUNT(b.booking_id) > 0 AND COUNT(b.booking_id) < ap.capacity * 0.40
    ORDER BY passenger_count ASC
    LIMIT 15
"""

cursor.execute(query)
underperforming = cursor.fetchall()

# datetime-Objekte zu strings konvertieren
for f in underperforming:
    if isinstance(f["departure_time"], datetime):
        f["departure_time"] = f["departure_time"].strftime("%Y-%m-%d %H:%M:%S")
    f["ticket_price"] = float(f["ticket_price"])

print(f"  {len(underperforming)} unterbelegte Fluege gefunden")

# Top-Performer zum Vergleich
print("Extrahiere bestausgelastete Fluege zum Vergleich...")
best_query = """
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
    WHERE f.departure BETWEEN '2015-06-01 00:00:00' AND '2015-06-07 23:59:59'
    GROUP BY f.flight_id, f.flightno, dep.name, arr.name, f.departure, ap.capacity
    HAVING COUNT(b.booking_id) > 0
    ORDER BY load_factor DESC
    LIMIT 10
"""
cursor.execute(best_query)
best_performers = cursor.fetchall()

for f in best_performers:
    if isinstance(f["departure_time"], datetime):
        f["departure_time"] = f["departure_time"].strftime("%Y-%m-%d %H:%M:%S")
    f["avg_price"] = float(f["avg_price"])
    f["load_factor"] = float(f["load_factor"])

print(f"  {len(best_performers)} Top-Performer gefunden")

# Wochenstatistik
print("Extrahiere Wochenstatistik...")
stats_query = """
    SELECT COUNT(DISTINCT f.flight_id) as total_flights,
           SUM(sub.pax) as total_passengers,
           AVG(sub.pax) as avg_passengers_per_flight,
           AVG(sub.load_pct) as avg_load_factor
    FROM flight f
    JOIN airplane ap ON f.airplane_id = ap.airplane_id
    JOIN (
        SELECT b.flight_id, COUNT(*) as pax,
               COUNT(*) * 100.0 / ap2.capacity as load_pct
        FROM booking b
        JOIN flight f2 ON b.flight_id = f2.flight_id
        JOIN airplane ap2 ON f2.airplane_id = ap2.airplane_id
        WHERE f2.departure BETWEEN '2015-06-01 00:00:00' AND '2015-06-07 23:59:59'
        GROUP BY b.flight_id, ap2.capacity
    ) sub ON f.flight_id = sub.flight_id
    WHERE f.departure BETWEEN '2015-06-01 00:00:00' AND '2015-06-07 23:59:59'
"""
cursor.execute(stats_query)
weekly_stats = cursor.fetchone()
for k, v in weekly_stats.items():
    if v is not None:
        weekly_stats[k] = float(v) if not isinstance(v, int) else v

print(f"  Wochenstatistik: {weekly_stats['total_flights']} Fluege, "
      f"Durchschnitt {weekly_stats['avg_load_factor']:.1f}% Auslastung")

cursor.close()
conn.close()

# Python-Modul generieren
print("\nGeneriere flight_data.py ...")

output = '''"""
Vorberechneter Datenauszug aus der Datenbank flughafendb_large.
Extrahiert am: ''' + datetime.now().strftime("%Y-%m-%d %H:%M") + '''

Datenbank-Groesse: 462'553 Fluege, 54'304'619 Buchungen
Zeitraum: 1. bis 7. Juni 2015

Dieser Datenauszug vermeidet die langsamen Queries ueber die 54-Millionen-Buchungstabelle
und ermoeglicht einen sofortigen Start der Streamlit-App.
"""

# Top 15 unterbelegte Fluege (Auslastung < 40%)
UNDERPERFORMING_FLIGHTS = '''

output += json.dumps(underperforming, indent=4, ensure_ascii=False, default=str)

output += '''

# Top 10 bestausgelastete Fluege (zum Vergleich fuer die Analyse)
BEST_PERFORMING_FLIGHTS = '''

output += json.dumps(best_performers, indent=4, ensure_ascii=False, default=str)

output += '''

# Wochenstatistik (Gesamtueberblick)
WEEKLY_STATS = '''

output += json.dumps(weekly_stats, indent=4, ensure_ascii=False, default=str)

output += '''

def get_underperforming_flights(limit=5):
    """Gibt die am schlechtesten ausgelasteten Fluege zurueck."""
    return UNDERPERFORMING_FLIGHTS[:limit]

def get_best_performing_flights(limit=5):
    """Gibt die am besten ausgelasteten Fluege zurueck."""
    return BEST_PERFORMING_FLIGHTS[:limit]

def get_weekly_stats():
    """Gibt die Wochenstatistik zurueck."""
    return WEEKLY_STATS
'''

with open("flight_data.py", "w", encoding="utf-8") as f:
    f.write(output)

print("flight_data.py erfolgreich erstellt!")
print("\nVorschau der unterbelegten Fluege:")
for f in underperforming[:5]:
    load = (f["passenger_count"] / f["capacity"]) * 100
    print(f"  {f['flightno']}: {f['route']}, {f['passenger_count']}/{f['capacity']} ({load:.0f}%), "
          f"Preis: {f['ticket_price']:.2f} CHF")
