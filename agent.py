import urllib.request
import urllib.error
import json
import copy

# Versuche mysql.connector zu importieren (optional, fuer Live-Optimierungen)
try:
    import mysql.connector
    HAS_MYSQL = True
except ImportError:
    HAS_MYSQL = False

# Datenbank Verbindungseinstellungen
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Startup.6"
DB_NAME = "flughafendb_large"

# Ollama API Konfiguration
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "phi3"

# Vorberechneter Datenauszug importieren
try:
    from flight_data import get_underperforming_flights, get_best_performing_flights, get_weekly_stats
    HAS_EXTRACTED_DATA = True
except ImportError:
    HAS_EXTRACTED_DATA = False


class FlightOptimizationAgent:
    def __init__(self):
        self.host = DB_HOST
        self.user = DB_USER
        self.password = DB_PASSWORD
        self.database = DB_NAME
        # Lokaler Speicher fuer Optimierungen (wenn kein DB-Zugriff)
        self._optimized_flights = set()

    def get_db_connection(self):
        if not HAS_MYSQL:
            raise ConnectionError("mysql.connector ist nicht installiert.")
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def fetch_flight_data(self):
        """Laedt Flugdaten – bevorzugt aus dem Datenauszug, sonst aus der DB."""
        if HAS_EXTRACTED_DATA:
            # Sofortiges Laden aus dem vorberechneten Datenauszug
            return copy.deepcopy(get_underperforming_flights(limit=5))
        
        # Fallback: Live-Query (langsam bei grossen Datenbanken)
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
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

    def fetch_route_context(self):
        """Holt Kontextdaten – bevorzugt aus dem Datenauszug."""
        if HAS_EXTRACTED_DATA:
            best_flights = get_best_performing_flights(limit=5)
            weekly_stats = get_weekly_stats()
            return {
                "weekly_stats": weekly_stats,
                "best_flights": best_flights
            }
        
        # Fallback: Live-Query
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            context_query = """
                SELECT COUNT(DISTINCT f.flight_id) as total_flights_week,
                       AVG(sub.passenger_count) as avg_passengers,
                       AVG(sub.load_factor) as avg_load_factor
                FROM flight f
                JOIN (
                    SELECT b.flight_id,
                           COUNT(b.booking_id) as passenger_count,
                           COUNT(b.booking_id) / ap2.capacity * 100 as load_factor
                    FROM booking b
                    JOIN flight f2 ON b.flight_id = f2.flight_id
                    JOIN airplane ap2 ON f2.airplane_id = ap2.airplane_id
                    WHERE f2.departure BETWEEN '2015-06-01 00:00:00' AND '2015-06-07 23:59:59'
                    GROUP BY b.flight_id, ap2.capacity
                ) sub ON f.flight_id = sub.flight_id
                WHERE f.departure BETWEEN '2015-06-01 00:00:00' AND '2015-06-07 23:59:59'
            """
            cursor.execute(context_query)
            context = cursor.fetchone()
        except Exception:
            context = {"total_flights_week": 0, "avg_passengers": 0, "avg_load_factor": 0}
        
        try:
            best_query = """
                SELECT f.flightno,
                       CONCAT(dep.name, ' nach ', arr.name) as route,
                       ap.capacity,
                       COUNT(b.booking_id) as passenger_count,
                       ROUND(COUNT(b.booking_id) / ap.capacity * 100, 1) as load_factor
                FROM flight f
                JOIN airport dep ON f.`from` = dep.airport_id
                JOIN airport arr ON f.`to` = arr.airport_id
                JOIN airplane ap ON f.airplane_id = ap.airplane_id
                LEFT JOIN booking b ON b.flight_id = f.flight_id
                WHERE f.departure BETWEEN '2015-06-01 00:00:00' AND '2015-06-07 23:59:59'
                GROUP BY f.flight_id, f.flightno, dep.name, arr.name, ap.capacity
                HAVING COUNT(b.booking_id) > 0
                ORDER BY load_factor DESC
                LIMIT 5
            """
            cursor.execute(best_query)
            best_flights = cursor.fetchall()
        except Exception:
            best_flights = []
        
        cursor.close()
        conn.close()
        return {"weekly_stats": context, "best_flights": best_flights}

    def optimize_flight(self, flight_id):
        """Optimiert einen Flug – DB-basiert oder lokal simuliert."""
        try:
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
        except Exception:
            # Lokale Simulation wenn DB nicht erreichbar
            self._optimized_flights.add(flight_id)

    def reset_flight(self, flight_id):
        """Setzt Flug-Optimierung zurueck – DB-basiert oder lokal."""
        try:
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
        except Exception:
            self._optimized_flights.discard(flight_id)

    def is_flight_optimized(self, flight_id):
        """Prueft ob ein Flug bereits optimiert wurde."""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM booking WHERE booking_id >= 10000000 AND flight_id = %s",
                (flight_id,)
            )
            has_simulated = cursor.fetchone()[0] > 0
            cursor.close()
            conn.close()
            return has_simulated
        except Exception:
            return flight_id in self._optimized_flights

    def _generate_rule_based_analysis(self, flights_with_kpis):
        """Generiert eine datenbasierte Analyse ohne LLM.
        Analysiert die tatsaechlichen Flugdaten und gibt konkrete Empfehlungen."""
        
        if not flights_with_kpis:
            return "Keine Flugdaten verfuegbar fuer die Analyse."
        
        # Daten analysieren
        worst = min(flights_with_kpis, key=lambda f: f["load_factor"])
        best = max(flights_with_kpis, key=lambda f: f["load_factor"])
        avg_load = sum(f["load_factor"] for f in flights_with_kpis) / len(flights_with_kpis)
        total_revenue = sum(f["revenue"] for f in flights_with_kpis)
        total_passengers = sum(f["passenger_count"] for f in flights_with_kpis)
        total_capacity = sum(f["capacity"] for f in flights_with_kpis)
        
        # Kontextdaten holen
        try:
            context = self.fetch_route_context()
            weekly_stats = context.get("weekly_stats", {})
            best_flights = context.get("best_flights", [])
        except Exception:
            weekly_stats = {}
            best_flights = []
        
        # Routen zaehlen
        route_counts = {}
        for f in flights_with_kpis:
            route = f["route"]
            if route not in route_counts:
                route_counts[route] = []
            route_counts[route].append(f)
        
        repeated_routes = {r: flights for r, flights in route_counts.items() if len(flights) > 1}
        
        # Potenzialberechnung
        potential_revenue = 0
        for f in flights_with_kpis:
            target_passengers = int(f["capacity"] * 0.80)
            extra_passengers = max(target_passengers - f["passenger_count"], 0)
            potential_revenue += extra_passengers * float(f["ticket_price"])
        
        # Analyse-Text zusammenbauen
        analysis = "Regelbasierte Analyse (LLM nicht verfuegbar)\n\n"
        
        analysis += "ZUSAMMENFASSUNG\n"
        analysis += (
            f"Es wurden {len(flights_with_kpis)} unterbelegte Fluege in der ersten Juniwoche 2015 "
            f"identifiziert. Die durchschnittliche Auslastung dieser Fluege liegt bei {avg_load:.1f}%, "
            f"was deutlich unter dem wirtschaftlich sinnvollen Schwellenwert von 70% liegt. "
            f"Der Gesamtumsatz dieser Fluege betraegt {total_revenue:,.2f} CHF bei insgesamt "
            f"{total_passengers} Passagieren auf {total_capacity} verfuegbaren Plaetzen.\n\n"
        )
        
        # Kontext: Vergleich mit Gesamtwoche
        if weekly_stats and weekly_stats.get("total_flights_week"):
            week_avg_load = weekly_stats.get("avg_load_factor", 0)
            if week_avg_load:
                analysis += "EINORDNUNG IM WOCHENKONTEXT\n"
                analysis += (
                    f"In der gesamten Woche wurden {int(weekly_stats['total_flights_week'])} Fluege durchgefuehrt "
                    f"mit einer durchschnittlichen Auslastung von {float(week_avg_load):.1f}%. "
                    f"Die hier analysierten Fluege liegen mit {avg_load:.1f}% deutlich unter diesem Durchschnitt. "
                )
                if best_flights:
                    best_load = best_flights[0].get("load_factor", 0)
                    analysis += (
                        f"Zum Vergleich: Die bestausgelasteten Fluege der Woche erreichen bis zu "
                        f"{float(best_load):.1f}% Auslastung.\n\n"
                    )
                else:
                    analysis += "\n\n"
        
        analysis += "KRITISCHSTER FLUG\n"
        analysis += (
            f"Flug {worst['flightno']} auf der Route {worst['route']} weist mit {worst['load_factor']:.1f}% "
            f"die tiefste Auslastung auf. Bei einer Kapazitaet von {worst['capacity']} Plaetzen sind nur "
            f"{worst['passenger_count']} belegt. Der aktuelle Umsatz betraegt {worst['revenue']:,.2f} CHF "
            f"bei einem Durchschnittspreis von {float(worst['ticket_price']):.2f} CHF.\n\n"
        )
        
        if repeated_routes:
            analysis += "ERKANNTE MUSTER\n"
            for route, flights in repeated_routes.items():
                avg_route_load = sum(f["load_factor"] for f in flights) / len(flights)
                analysis += (
                    f"Die Route '{route}' erscheint {len(flights)} Mal in der Liste der unterbelegten Fluege "
                    f"mit einer durchschnittlichen Auslastung von {avg_route_load:.1f}%. "
                    f"Dies deutet auf ein systematisches Nachfrageproblem auf dieser Strecke hin.\n"
                )
            analysis += "\n"
        
        analysis += "WIRTSCHAFTLICHE BERECHNUNG\n"
        analysis += (
            f"Wuerden alle {len(flights_with_kpis)} unterbelegten Fluege eine Auslastung von 80% erreichen, "
            f"ergaebe sich ein zusaetzliches Umsatzpotenzial von {potential_revenue:,.2f} CHF. "
            f"Selbst bei einer Preisreduktion von 20% zur Nachfragestimulation betraegt das Nettopotenzial "
            f"noch {potential_revenue * 0.8:,.2f} CHF.\n\n"
        )
        
        analysis += "HANDLUNGSEMPFEHLUNGEN\n"
        analysis += (
            f"1. Preisanpassung: Fuer den kritischsten Flug {worst['flightno']} wird eine Preissenkung "
            f"um 20% empfohlen, um die Nachfrage zu stimulieren.\n"
            f"2. Kapazitaetsanpassung: Pruefen Sie, ob auf der Route {worst['route']} ein kleineres "
            f"Flugzeug eingesetzt werden kann, um die Fixkosten zu senken.\n"
        )
        
        if repeated_routes:
            for route in repeated_routes:
                analysis += (
                    f"3. Frequenzreduktion: Auf der Route '{route}' sollte eine Reduktion der Flugfrequenz "
                    f"in Betracht gezogen werden, da mehrere Fluege unterbelegt sind.\n"
                )
        
        analysis += (
            f"\nGesamtbewertung: Die analysierten Fluege zeigen ein klares Optimierungspotenzial. "
            f"Eine Kombination aus gezielter Preisanpassung und Kapazitaetsoptimierung kann den Umsatz "
            f"dieser Routen um bis zu {(potential_revenue / max(total_revenue, 1)) * 100:.0f}% steigern."
        )
        
        return analysis

    def generate_analysis(self, flights_with_kpis):
        """Generiert eine LLM-gestuetzte Analyse der Flugdaten.
        Bei Nichterreichbarkeit von Ollama wird ein regelbasierter Fallback verwendet."""
        
        if not flights_with_kpis:
            return "Keine Flugdaten fuer die Analyse verfuegbar."
        
        # Aggregierte Statistiken berechnen
        avg_load = sum(f["load_factor"] for f in flights_with_kpis) / len(flights_with_kpis)
        min_load = min(f["load_factor"] for f in flights_with_kpis)
        max_load = max(f["load_factor"] for f in flights_with_kpis)
        total_revenue = sum(f["revenue"] for f in flights_with_kpis)
        total_passengers = sum(f["passenger_count"] for f in flights_with_kpis)
        total_capacity = sum(f["capacity"] for f in flights_with_kpis)
        
        # Kontextdaten holen
        try:
            context = self.fetch_route_context()
            weekly_stats = context.get("weekly_stats", {})
            best_flights = context.get("best_flights", [])
        except Exception:
            weekly_stats = {}
            best_flights = []
        
        # Strukturierter Prompt
        prompt = (
            "Du bist ein erfahrener Airline-Revenue-Management-Analyst. "
            "Analysiere die folgenden realen Flugdaten aus der ersten Juniwoche 2015 "
            "und erstelle eine detaillierte, datengestuetzte Analyse.\n\n"
        )
        
        prompt += "=== AGGREGIERTE KENNZAHLEN ===\n"
        prompt += f"Anzahl analysierter Fluege: {len(flights_with_kpis)}\n"
        prompt += f"Durchschnittliche Auslastung: {avg_load:.1f}%\n"
        prompt += f"Tiefste Auslastung: {min_load:.1f}%\n"
        prompt += f"Hoechste Auslastung: {max_load:.1f}%\n"
        prompt += f"Gesamtumsatz: {total_revenue:,.2f} CHF\n"
        prompt += f"Gesamtpassagiere: {total_passengers} von {total_capacity} Plaetzen\n"
        prompt += f"Gesamtauslastung: {(total_passengers / max(total_capacity, 1)) * 100:.1f}%\n\n"
        
        prompt += "=== EINZELNE FLUEGE (UNTERBELEGT) ===\n"
        for f in flights_with_kpis:
            prompt += (
                f"Flug {f['flightno']}: Route {f['route']}, "
                f"Kapazitaet {f['capacity']}, Passagiere {f['passenger_count']}, "
                f"Durchschnittspreis {float(f['ticket_price']):.2f} CHF, "
                f"Auslastung {f['load_factor']}%, Umsatz {f['revenue']:,.2f} CHF\n"
            )
        
        if weekly_stats and weekly_stats.get("total_flights_week"):
            prompt += f"\n=== WOCHENKONTEXT ===\n"
            prompt += f"Gesamtanzahl Fluege in der Woche: {weekly_stats.get('total_flights_week', 'N/A')}\n"
            avg_pax = weekly_stats.get('avg_passengers', weekly_stats.get('avg_passengers_per_flight', 'N/A'))
            prompt += f"Durchschnittliche Passagierzahl (alle Fluege): {avg_pax}\n"
            prompt += f"Durchschnittliche Auslastung (alle Fluege): {weekly_stats.get('avg_load_factor', 'N/A')}%\n"
        
        if best_flights:
            prompt += "\n=== TOP 5 BESTAUSGELASTETE FLUEGE (VERGLEICH) ===\n"
            for bf in best_flights:
                prompt += (
                    f"Flug {bf.get('flightno', 'N/A')}: Route {bf.get('route', 'N/A')}, "
                    f"Kapazitaet {bf.get('capacity', 'N/A')}, Passagiere {bf.get('passenger_count', 'N/A')}, "
                    f"Auslastung {bf.get('load_factor', 'N/A')}%\n"
                )
        
        prompt += (
            "\n=== ANALYSEANWEISUNGEN ===\n"
            "Erstelle eine strukturierte Analyse mit folgenden Abschnitten:\n\n"
            "1. ZUSAMMENFASSUNG: Kurze Uebersicht der Situation (2 bis 3 Saetze)\n\n"
            "2. ERKANNTE MUSTER: Welche Muster erkennst du?\n"
            "   Gibt es Routen die mehrfach unterbelegt sind?\n"
            "   Gibt es Zusammenhaenge mit Tageszeiten oder Kapazitaeten?\n"
            "   Wie verhalten sich diese Fluege im Vergleich zu den bestausgelasteten?\n\n"
            "3. RISIKOANALYSE: Welche Risiken bestehen?\n"
            "   Was passiert wenn keine Massnahmen ergriffen werden?\n"
            "   Welche Routen sind am staerksten gefaehrdet?\n\n"
            "4. WIRTSCHAFTLICHE BERECHNUNG:\n"
            "   Berechne das Umsatzpotenzial wenn die Fluege 80% Auslastung erreichen wuerden.\n"
            "   Beruecksichtige dabei eine moegliche Preisreduktion von 20%.\n"
            "   Zeige die konkreten Zahlen.\n\n"
            "5. HANDLUNGSEMPFEHLUNGEN: Konkrete, priorisierte Massnahmen mit erwarteter Wirkung.\n\n"
            "Verwende Schweizer Rechtschreibung (ss statt scharfem s). "
            "Verwende KEINE Emojis. Sei praezise und datengestuetzt."
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
            with urllib.request.urlopen(req, timeout=120) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                return res_json.get("response", "Keine Antwort von Ollama erhalten.")
        except Exception:
            return self._generate_rule_based_analysis(flights_with_kpis)
