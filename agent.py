import urllib.request
import urllib.error
import json
import mysql.connector

# Datenbank Verbindungseinstellungen
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Startup.6"
DB_NAME = "flughafendb_large"

# Ollama API Konfiguration
# Falls Ollama nicht erreichbar ist, greift das Skript auf eine simulierte Analyse zurück.
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "phi3"

class FlightOptimizationAgent:
    def __init__(self):
        self.host = DB_HOST
        self.user = DB_USER
        self.password = DB_PASSWORD
        self.database = DB_NAME

    def get_db_connection(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def fetch_flight_data(self):
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Suche nach unterausgelasteten Flügen in der ersten Juniwoche 2015
        query = """
            SELECT f.flight_id as id, 
                   f.flightno,
                   CONCAT(dep.name, ' nach ', arr.name) as route,
                   f.departure as departure_time,
                   ap.capacity,
                   (SELECT COUNT(*) FROM booking b WHERE b.flight_id = f.flight_id) as passenger_count,
                   COALESCE((SELECT AVG(b.price) FROM booking b WHERE b.flight_id = f.flight_id), 0.0) as ticket_price
            FROM flight f
            JOIN airport dep ON f.from = dep.airport_id
            JOIN airport arr ON f.to = arr.airport_id
            JOIN airplane ap ON f.airplane_id = ap.airplane_id
            WHERE f.departure BETWEEN '2015-06-01 00:00:00' AND '2015-06-07 23:59:59'
            GROUP BY f.flight_id
            HAVING passenger_count > 0 AND passenger_count < ap.capacity * 0.40
            ORDER BY passenger_count ASC
            LIMIT 5
        """
        cursor.execute(query)
        flights = cursor.fetchall()
        cursor.close()
        conn.close()
        return flights

    def calculate_kpis(self, flights):
        for flight in flights:
            capacity = flight["capacity"]
            passengers = flight["passenger_count"]
            price = float(flight["ticket_price"])
            
            # Auslastungsrate berechnen
            load_factor = (passengers / capacity) * 100 if capacity > 0 else 0.0
            flight["load_factor"] = round(load_factor, 2)
            
            # Umsatz berechnen
            revenue = passengers * price
            flight["revenue"] = round(revenue, 2)
        return flights

    def optimize_flight(self, flight_id):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # 1. Bestehende Ticketpreise um 20% senken
        cursor.execute(
            "UPDATE booking SET price = price * 0.8 WHERE flight_id = %s",
            (flight_id,)
        )
        
        # 2. Neue Buchungen simulieren
        cursor.execute("""
            SELECT ap.capacity, 
                   (SELECT COUNT(*) FROM booking WHERE flight_id = %s) as passenger_count
            FROM flight f
            JOIN airplane ap ON f.airplane_id = ap.airplane_id
            WHERE f.flight_id = %s
        """, (flight_id, flight_id))
        row = cursor.fetchone()
        
        if row:
            capacity, passenger_count = row
            target_passengers = int(capacity * 0.85)
            extra_needed = max(target_passengers - passenger_count, 10)
            
            start_booking_id = 10000000 + flight_id * 1000
            
            cursor.execute("SELECT AVG(price) FROM booking WHERE flight_id = %s", (flight_id,))
            avg_price_row = cursor.fetchone()
            new_price = float(avg_price_row[0]) if avg_price_row and avg_price_row[0] else 150.00
            
            new_bookings = []
            for i in range(extra_needed):
                new_bookings.append((
                    start_booking_id + i,
                    flight_id,
                    f"{10+i}X",
                    i + 1,
                    new_price
                ))
                
            insert_query = """
                INSERT INTO booking (booking_id, flight_id, seat, passenger_id, price)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.executemany(insert_query, new_bookings)
            conn.commit()
            
        cursor.close()
        conn.close()

    def reset_flight(self, flight_id):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM booking WHERE booking_id >= 10000000 AND flight_id = %s",
            (flight_id,)
        )
        
        cursor.execute(
            "UPDATE booking SET price = price / 0.8 WHERE flight_id = %s",
            (flight_id,)
        )
        conn.commit()
        
        cursor.close()
        conn.close()

    def generate_analysis(self, flights_with_kpis):
        # Strukturierter Prompt für das LLM zur Generierung des Denkprozesses
        prompt = (
            "Du bist ein agentischer Optimierungsanalyst für ein Flughafenszenario.\n"
            "Analysiere die folgenden realen Flugdaten und berechneten KPIs:\n\n"
        )
        for f in flights_with_kpis:
            prompt += (
                f"Flug ID {f['id']}: Route {f['route']}, Flugnummer {f['flightno']}, "
                f"Kapazität {f['capacity']}, Passagiere {f['passenger_count']}, "
                f"Durchschnittspreis {f['ticket_price']} CHF, Auslastung {f['load_factor']}%, "
                f"Umsatz {f['revenue']} CHF\n"
            )
        
        prompt += (
            "\nFühre eine strukturierte Analyse durch und halte dich strikt an diese Regeln:\n"
            "1. Verwende Schweizer Rechtschreibung (kein scharfes s, sondern ss nutzen).\n"
            "2. Verwende KEINE Emojis und KEINE Gedankenstriche (wie - oder –) in deiner Antwort.\n"
            "3. Zeige deinen Denkprozess (Chain of Thought): Welche Muster erkennst du auf der Route?\n"
            "4. Begründe, welche Entscheidungen Sinn machen (z.B. Preisanpassungen, Kapazitätsanpassungen oder Flugstreichungen).\n"
            "5. Schliesse mit einer konkreten, eindeutigen Handlungsempfehlung ab.\n"
        )

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        url = OLLAMA_URL
        if not url.endswith("/api/generate"):
            url = url.rstrip("/") + "/api/generate"
            
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                return res_json.get("response", "Keine Antwort von Ollama erhalten.")
        except Exception:
            mock_analysis = (
                "Denkprozess des Agenten (Simulierter Modus):\n"
                "Bei der Analyse der Flugdaten der ersten Juniwoche fällt auf, dass mehrere Flüge eine ungenügende Auslastungsrate aufweisen. "
                "Besonders kritisch ist der Flug mit der tiefsten Auslastung. Hier liegt die Auslastungsrate bei unter 30 Prozent. "
                "Ein so tiefer Wert drückt den Gesamtumsatz der jeweiligen Route massiv und deutet auf eine Ineffizienz hin.\n\n"
                "Mögliche Massnahmen zur Optimierung:\n"
                "Eine Streichung von Flügen ist kurzfristig oft schwer umsetzbar. "
                "Eine gezielte Preisanpassung erscheint sinnvoller. Durch eine Preissenkung um 20 Prozent können freie Plätze vermarktet werden. "
                "Dies stimuliert die Nachfrage und erhöht die Auslastung auf den angestrebten Zielwert von über 80 Prozent, was den Umsatz stabilisiert.\n\n"
                "Empfehlung:\n"
                "Es wird empfohlen, für den am schlechtesten ausgelasteten Flug eine Preisminderung um 20 Prozent durchzuführen und die Nachfrage zu beobachten."
            )
            return mock_analysis
