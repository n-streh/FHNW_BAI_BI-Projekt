import urllib.request
import urllib.error
import json
import copy
from datetime import datetime

try:
    import mysql.connector
    HAS_MYSQL = True
except ImportError:
    HAS_MYSQL = False

from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "phi3"
OLLAMA_TIMEOUT = 300
OLLAMA_NUM_PREDICT = 700

PRICE_REDUCTION = 0.20
TARGET_LOAD_FACTOR = 0.85
MIN_EXTRA_PASSENGERS = 10

try:
    from flight_data import (
        get_underperforming_flights,
        get_best_performing_flights,
        get_weekly_stats,
        get_period_presets,
        get_period_data,
        is_period_preloaded,
    )
    HAS_EXTRACTED_DATA = True
except ImportError:
    HAS_EXTRACTED_DATA = False


class FlightOptimizationAgent:
    def __init__(self):
        self.host = DB_HOST
        self.user = DB_USER
        self.password = DB_PASSWORD
        self.database = DB_NAME
        self._local_optimizations = {}
        self.current_period = "7d"
        self.last_llm_error = None
        self.last_analysis_source = None

    def get_period_info(self, period=None):
        period = period or self.current_period
        if HAS_EXTRACTED_DATA:
            return get_period_presets().get(period, {})
        return {
            "label": "1 Woche",
            "start": "2015-06-01",
            "end": "2015-06-07",
            "preloaded": False,
            "slow_hint": "Live-Abfrage gegen MySQL",
        }

    def set_period(self, period):
        if period != self.current_period:
            self.current_period = period
            self._local_optimizations = {}

    def _normalize_weekly_stats(self, stats):
        if not stats:
            return {}
        return {
            "total_flights_week": stats.get("total_flights_week") or stats.get("total_flights"),
            "avg_passengers": stats.get("avg_passengers") or stats.get("avg_passengers_per_flight"),
            "avg_load_factor": stats.get("avg_load_factor"),
        }

    def _simulate_optimization(self, flight):
        capacity = flight["capacity"]
        passenger_count = flight["passenger_count"]
        original_price = float(flight["ticket_price"])
        target_passengers = int(capacity * TARGET_LOAD_FACTOR)
        extra_needed = max(target_passengers - passenger_count, MIN_EXTRA_PASSENGERS)
        new_passenger_count = min(passenger_count + extra_needed, capacity)
        new_ticket_price = original_price * (1 - PRICE_REDUCTION)

        optimized = copy.deepcopy(flight)
        optimized["passenger_count"] = new_passenger_count
        optimized["ticket_price"] = round(new_ticket_price, 2)
        return optimized

    def get_optimization_details(self, flight_id):
        baseline = self.get_baseline_flight(flight_id)
        if not baseline:
            return None

        original = self.calculate_kpis([copy.deepcopy(baseline)])[0]
        optimized = self.calculate_kpis([self._simulate_optimization(baseline)])[0]
        extra_passengers = optimized["passenger_count"] - original["passenger_count"]

        return {
            "flightno": original["flightno"],
            "route": original["route"],
            "capacity": original["capacity"],
            "price_before": float(original["ticket_price"]),
            "price_after": float(optimized["ticket_price"]),
            "price_reduction_pct": PRICE_REDUCTION * 100,
            "passengers_before": original["passenger_count"],
            "passengers_added": extra_passengers,
            "passengers_after": optimized["passenger_count"],
            "target_load_pct": TARGET_LOAD_FACTOR * 100,
            "load_before": original["load_factor"],
            "load_after": optimized["load_factor"],
            "revenue_before": original["revenue"],
            "revenue_after": optimized["revenue"],
            "revenue_delta": round(optimized["revenue"] - original["revenue"], 2),
            "formula_revenue_before": f"{original['passenger_count']} x {original['ticket_price']:.2f} CHF",
            "formula_revenue_after": f"{optimized['passenger_count']} x {optimized['ticket_price']:.2f} CHF",
            "steps": [
                f"Durchschnittspreis um {PRICE_REDUCTION * 100:.0f} % senken: "
                f"{original['ticket_price']:.2f} -> {optimized['ticket_price']:.2f} CHF",
                f"Zusaetzliche Passagiere simulieren: +{extra_passengers} "
                f"(Ziel: {TARGET_LOAD_FACTOR * 100:.0f} % von {original['capacity']} Plaetzen, "
                f"mindestens +{MIN_EXTRA_PASSENGERS})",
                f"Neue Auslastung: {optimized['passenger_count']}/{optimized['capacity']} "
                f"= {optimized['load_factor']:.1f} %",
                f"Neuer Umsatz: {optimized['passenger_count']} x {optimized['ticket_price']:.2f} CHF "
                f"= {optimized['revenue']:,.2f} CHF",
            ],
        }

    def _apply_local_optimizations(self, flights):
        result = []
        for flight in flights:
            flight_id = flight["id"]
            if flight_id in self._local_optimizations:
                result.append(copy.deepcopy(self._local_optimizations[flight_id]))
            else:
                result.append(flight)
        return result

    def get_db_connection(self):
        if not HAS_MYSQL:
            raise ConnectionError("mysql.connector ist nicht installiert.")
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
        )

    def _date_range_sql(self, period=None):
        info = self.get_period_info(period)
        start = info.get("start", "2015-06-01")
        end = info.get("end", "2015-06-07")
        return f"{start} 00:00:00", f"{end} 23:59:59"

    def _fetch_live_flights(self, period=None, limit=5):
        start, end = self._date_range_sql(period)
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
            WHERE f.departure BETWEEN %s AND %s
            GROUP BY f.flight_id, f.flightno, dep.name, arr.name, f.departure, ap.capacity
            HAVING COUNT(b.booking_id) > 0 AND COUNT(b.booking_id) < ap.capacity * 0.40
            ORDER BY passenger_count ASC
            LIMIT %s
        """
        cursor.execute(query, (start, end, limit))
        flights = cursor.fetchall()
        for flight in flights:
            if isinstance(flight.get("departure_time"), datetime):
                flight["departure_time"] = flight["departure_time"].strftime("%Y-%m-%d %H:%M:%S")
            flight["ticket_price"] = float(flight["ticket_price"])
        cursor.close()
        conn.close()
        return flights

    def _fetch_live_context(self, period=None):
        start, end = self._date_range_sql(period)
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)

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
                WHERE f2.departure BETWEEN %s AND %s
                GROUP BY b.flight_id, ap2.capacity
            ) sub ON f.flight_id = sub.flight_id
            WHERE f.departure BETWEEN %s AND %s
        """
        cursor.execute(context_query, (start, end, start, end))
        context = cursor.fetchone() or {}

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
            WHERE f.departure BETWEEN %s AND %s
            GROUP BY f.flight_id, f.flightno, dep.name, arr.name, ap.capacity
            HAVING COUNT(b.booking_id) > 0
            ORDER BY load_factor DESC
            LIMIT 5
        """
        cursor.execute(best_query, (start, end))
        best_flights = cursor.fetchall()
        cursor.close()
        conn.close()
        return {
            "weekly_stats": self._normalize_weekly_stats(context),
            "best_flights": best_flights,
        }

    def fetch_flight_data(self, period=None):
        period = period or self.current_period
        period_data = get_period_data(period) if HAS_EXTRACTED_DATA else None

        if period_data is not None:
            flights = copy.deepcopy(period_data.get("underperforming", [])[:5])
            return self._apply_local_optimizations(flights)

        if HAS_EXTRACTED_DATA and is_period_preloaded(period):
            flights = copy.deepcopy(get_underperforming_flights(limit=5))
            return self._apply_local_optimizations(flights)

        flights = self._fetch_live_flights(period)
        return self._apply_local_optimizations(flights)

    def calculate_kpis(self, flights):
        for flight in flights:
            capacity = flight["capacity"]
            passengers = flight["passenger_count"]
            price = float(flight["ticket_price"])
            load_factor = (passengers / capacity) * 100 if capacity > 0 else 0.0
            flight["load_factor"] = round(load_factor, 2)
            flight["revenue"] = round(passengers * price, 2)
        return flights

    def _has_geo(self, flight):
        keys = ("dep_lat", "dep_lon", "arr_lat", "arr_lon")
        return all(flight.get(k) is not None for k in keys)

    def _fetch_geo_for_flights(self, flight_ids):
        if not flight_ids or not HAS_MYSQL:
            return {}
        placeholders = ",".join(["%s"] * len(flight_ids))
        query = f"""
            SELECT f.flight_id as id,
                   dep.name as dep_name,
                   arr.name as arr_name,
                   dep_geo.latitude as dep_lat,
                   dep_geo.longitude as dep_lon,
                   dep_geo.country as dep_country,
                   arr_geo.latitude as arr_lat,
                   arr_geo.longitude as arr_lon,
                   arr_geo.country as arr_country
            FROM flight f
            JOIN airport dep ON f.`from` = dep.airport_id
            JOIN airport arr ON f.`to` = arr.airport_id
            LEFT JOIN airport_geo dep_geo ON dep.airport_id = dep_geo.airport_id
            LEFT JOIN airport_geo arr_geo ON arr.airport_id = arr_geo.airport_id
            WHERE f.flight_id IN ({placeholders})
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, tuple(flight_ids))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            result = {}
            for row in rows:
                geo = {}
                for key in (
                    "dep_name", "arr_name", "dep_country", "arr_country",
                    "dep_lat", "dep_lon", "arr_lat", "arr_lon",
                ):
                    if row.get(key) is not None:
                        geo[key] = float(row[key]) if "lat" in key or "lon" in key else row[key]
                result[row["id"]] = geo
            return result
        except Exception:
            return {}

    def enrich_flights_geography(self, flights):
        """Ergaenzt Koordinaten aus Datensatz oder per DB-Lookup (airport_geo)."""
        missing_ids = [f["id"] for f in flights if not self._has_geo(f)]
        geo_by_id = self._fetch_geo_for_flights(missing_ids) if missing_ids else {}

        for flight in flights:
            if self._has_geo(flight):
                continue
            geo = geo_by_id.get(flight["id"])
            if geo:
                flight.update(geo)
            elif "route" in flight and " nach " in flight["route"]:
                dep, arr = flight["route"].split(" nach ", 1)
                flight.setdefault("dep_name", dep.strip())
                flight.setdefault("arr_name", arr.strip())

        return flights

    def fetch_route_context(self, period=None):
        period = period or self.current_period
        period_data = get_period_data(period) if HAS_EXTRACTED_DATA else None

        if period_data is not None:
            return {
                "weekly_stats": self._normalize_weekly_stats(period_data.get("stats", {})),
                "best_flights": period_data.get("best", [])[:5],
            }

        if HAS_EXTRACTED_DATA and is_period_preloaded(period):
            return {
                "weekly_stats": self._normalize_weekly_stats(get_weekly_stats()),
                "best_flights": get_best_performing_flights(limit=5),
            }

        return self._fetch_live_context(period)

    def needs_live_query(self, period=None):
        period = period or self.current_period
        if HAS_EXTRACTED_DATA:
            return get_period_data(period) is None and not is_period_preloaded(period)
        return True

    def optimize_flight(self, flight_id):
        if HAS_EXTRACTED_DATA:
            baseline = self.get_baseline_flight(flight_id)
            if baseline:
                self._local_optimizations[flight_id] = self._simulate_optimization(baseline)
            return

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE booking SET price = price * %s WHERE flight_id = %s",
                (1 - PRICE_REDUCTION, flight_id),
            )
            cursor.execute(
                """
                SELECT ap.capacity,
                       (SELECT COUNT(*) FROM booking WHERE flight_id = %s) as passenger_count
                FROM flight f
                JOIN airplane ap ON f.airplane_id = ap.airplane_id
                WHERE f.flight_id = %s
                """,
                (flight_id, flight_id),
            )
            row = cursor.fetchone()
            if row:
                capacity, passenger_count = row
                target_passengers = int(capacity * TARGET_LOAD_FACTOR)
                extra_needed = max(target_passengers - passenger_count, MIN_EXTRA_PASSENGERS)
                start_booking_id = 10000000 + flight_id * 1000
                cursor.execute("SELECT AVG(price) FROM booking WHERE flight_id = %s", (flight_id,))
                avg_price_row = cursor.fetchone()
                new_price = float(avg_price_row[0]) if avg_price_row and avg_price_row[0] else 150.00
                new_bookings = [
                    (start_booking_id + i, flight_id, f"{10 + i}X", i + 1, new_price)
                    for i in range(extra_needed)
                ]
                cursor.executemany(
                    "INSERT INTO booking (booking_id, flight_id, seat, passenger_id, price) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    new_bookings,
                )
                conn.commit()
            cursor.close()
            conn.close()
        except Exception:
            baseline = self.get_baseline_flight(flight_id)
            if baseline:
                self._local_optimizations[flight_id] = self._simulate_optimization(baseline)

    def reset_flight(self, flight_id):
        if HAS_EXTRACTED_DATA:
            self._local_optimizations.pop(flight_id, None)
            return

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM booking WHERE booking_id >= 10000000 AND flight_id = %s",
                (flight_id,),
            )
            cursor.execute(
                "UPDATE booking SET price = price / %s WHERE flight_id = %s",
                (1 - PRICE_REDUCTION, flight_id),
            )
            conn.commit()
            cursor.close()
            conn.close()
        except Exception:
            self._local_optimizations.pop(flight_id, None)

    def get_baseline_flight(self, flight_id):
        period_data = get_period_data(self.current_period) if HAS_EXTRACTED_DATA else None
        source_flights = []

        if period_data is not None:
            source_flights = period_data.get("underperforming", [])
        elif HAS_EXTRACTED_DATA:
            source_flights = get_underperforming_flights(limit=15)

        flight = next((f for f in source_flights if f["id"] == flight_id), None)
        if flight:
            return copy.deepcopy(flight)

        try:
            live = self._fetch_live_flights(self.current_period, limit=15)
            flight = next((f for f in live if f["id"] == flight_id), None)
            return copy.deepcopy(flight) if flight else None
        except Exception:
            return None

    def is_flight_optimized(self, flight_id):
        if HAS_EXTRACTED_DATA:
            return flight_id in self._local_optimizations

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM booking WHERE booking_id >= 10000000 AND flight_id = %s",
                (flight_id,),
            )
            has_simulated = cursor.fetchone()[0] > 0
            cursor.close()
            conn.close()
            return has_simulated
        except Exception:
            return flight_id in self._local_optimizations

    def check_ollama_available(self):
        try:
            req = urllib.request.Request(f"{OLLAMA_URL.rstrip('/')}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status != 200:
                    return False, f"HTTP {response.status}"
                models = json.loads(response.read()).get("models", [])
                names = {m.get("name", "").split(":")[0] for m in models}
                if OLLAMA_MODEL.split(":")[0] not in names:
                    return False, f"Modell '{OLLAMA_MODEL}' nicht gefunden. Verfuegbar: {', '.join(names)}"
                return True, "OK"
        except Exception as exc:
            return False, str(exc)

    def _call_ollama(self, prompt):
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": OLLAMA_NUM_PREDICT,
                "temperature": 0.4,
            },
        }
        url = f"{OLLAMA_URL.rstrip('/')}/api/generate"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            return res_json.get("response", "").strip()

    def _generate_rule_based_analysis(self, flights_with_kpis):
        if not flights_with_kpis:
            return "Keine Flugdaten verfuegbar fuer die Analyse."

        worst = min(flights_with_kpis, key=lambda f: f["load_factor"])
        avg_load = sum(f["load_factor"] for f in flights_with_kpis) / len(flights_with_kpis)
        total_revenue = sum(f["revenue"] for f in flights_with_kpis)
        total_passengers = sum(f["passenger_count"] for f in flights_with_kpis)
        total_capacity = sum(f["capacity"] for f in flights_with_kpis)

        try:
            context = self.fetch_route_context()
            weekly_stats = context.get("weekly_stats", {})
            best_flights = context.get("best_flights", [])
        except Exception:
            weekly_stats = {}
            best_flights = []

        route_counts = {}
        for f in flights_with_kpis:
            route_counts.setdefault(f["route"], []).append(f)
        repeated_routes = {r: fl for r, fl in route_counts.items() if len(fl) > 1}

        potential_revenue = 0
        for f in flights_with_kpis:
            target_passengers = int(f["capacity"] * 0.80)
            extra_passengers = max(target_passengers - f["passenger_count"], 0)
            potential_revenue += extra_passengers * float(f["ticket_price"])

        period_info = self.get_period_info()
        period_label = period_info.get("label", "gewaehlter Zeitraum")

        analysis = "Regelbasierte Analyse (LLM nicht verfuegbar)\n\n"
        if self.last_llm_error:
            analysis += f"Hinweis: {self.last_llm_error}\n\n"

        analysis += "ZUSAMMENFASSUNG\n"
        analysis += (
            f"Es wurden {len(flights_with_kpis)} unterbelegte Fluege im Zeitraum "
            f"{period_label} identifiziert. Die durchschnittliche Auslastung liegt bei "
            f"{avg_load:.1f} %. Gesamtumsatz: {total_revenue:,.2f} CHF, "
            f"{total_passengers} Passagiere auf {total_capacity} Plaetzen.\n\n"
        )

        if weekly_stats and weekly_stats.get("total_flights_week"):
            week_avg_load = weekly_stats.get("avg_load_factor", 0)
            analysis += "EINORDNUNG IM ZEITRAUM\n"
            analysis += (
                f"Im Zeitraum wurden {int(weekly_stats['total_flights_week'])} Fluege durchgefuehrt "
                f"mit einer durchschnittlichen Auslastung von {float(week_avg_load):.1f} %. "
                f"Die analysierten Fluege liegen mit {avg_load:.1f} % deutlich darunter."
            )
            if best_flights:
                analysis += (
                    f" Top-Auslastung im Zeitraum: {float(best_flights[0].get('load_factor', 0)):.1f} %."
                )
            analysis += "\n\n"

        analysis += "KRITISCHSTER FLUG\n"
        analysis += (
            f"Flug {worst['flightno']} ({worst['route']}): {worst['load_factor']:.1f} % Auslastung, "
            f"Umsatz {worst['revenue']:,.2f} CHF.\n\n"
        )

        if repeated_routes:
            analysis += "ERKANNTE MUSTER\n"
            for route, flights in repeated_routes.items():
                avg_route_load = sum(f["load_factor"] for f in flights) / len(flights)
                analysis += f"- Route '{route}': {len(flights)}x unterbelegt, Ø {avg_route_load:.1f} %.\n"
            analysis += "\n"

        analysis += "WIRTSCHAFTLICHE BERECHNUNG\n"
        analysis += (
            f"Bei 80 % Zielauslastung: Potenzial {potential_revenue:,.2f} CHF, "
            f"nach 20 % Preisreduktion netto ca. {potential_revenue * 0.8:,.2f} CHF.\n\n"
        )

        analysis += "HANDLUNGSEMPFEHLUNGEN\n"
        analysis += (
            f"1. Preissenkung fuer Flug {worst['flightno']} pruefen.\n"
            f"2. Kapazitaet auf Route {worst['route']} anpassen.\n"
        )
        return analysis

    def generate_analysis(self, flights_with_kpis):
        if not flights_with_kpis:
            return "Keine Flugdaten fuer die Analyse verfuegbar."

        avg_load = sum(f["load_factor"] for f in flights_with_kpis) / len(flights_with_kpis)
        total_revenue = sum(f["revenue"] for f in flights_with_kpis)
        total_passengers = sum(f["passenger_count"] for f in flights_with_kpis)
        total_capacity = sum(f["capacity"] for f in flights_with_kpis)

        try:
            context = self.fetch_route_context()
            weekly_stats = context.get("weekly_stats", {})
            best_flights = context.get("best_flights", [])
        except Exception:
            weekly_stats = {}
            best_flights = []

        period_info = self.get_period_info()
        prompt = (
            "Du bist ein Airline-Revenue-Management-Analyst. "
            f"Analysiere unterbelegte Fluege fuer den Zeitraum {period_info.get('label', '')} "
            f"({period_info.get('start')} bis {period_info.get('end')}). "
            "Antworte auf Deutsch (Schweizer Rechtschreibung, ss statt Eszett). "
            "Keine Emojis. Maximal 500 Woerter.\n\n"
            f"KENNZAHLEN: {len(flights_with_kpis)} Fluege, Ø Auslastung {avg_load:.1f} %, "
            f"Umsatz {total_revenue:,.0f} CHF, {total_passengers}/{total_capacity} Plaetze.\n\n"
            "FLUEGE:\n"
        )
        for f in flights_with_kpis:
            prompt += (
                f"- {f['flightno']}: {f['route']}, {f['passenger_count']}/{f['capacity']} Pax, "
                f"{f['load_factor']:.1f} %, {f['revenue']:,.0f} CHF\n"
            )

        if weekly_stats.get("total_flights_week"):
            prompt += (
                f"\nBENCHMARK: {int(weekly_stats['total_flights_week'])} Fluege im Zeitraum, "
                f"Ø Auslastung {float(weekly_stats.get('avg_load_factor', 0)):.1f} %.\n"
            )
        if best_flights:
            prompt += f"Top-Flug: {best_flights[0].get('flightno')} mit {best_flights[0].get('load_factor')} %.\n"

        prompt += (
            "\nStruktur: 1) ZUSAMMENFASSUNG 2) MUSTER 3) RISIKO "
            "4) UMSATZPOTENZIAL (80 % Auslastung, -20 % Preis) 5) EMPFEHLUNGEN"
        )

        available, message = self.check_ollama_available()
        if not available:
            self.last_llm_error = message
            self.last_analysis_source = "fallback"
            return self._generate_rule_based_analysis(flights_with_kpis)

        try:
            response = self._call_ollama(prompt)
            if response:
                self.last_llm_error = None
                self.last_analysis_source = "llm"
                return response
            self.last_llm_error = "Leere Antwort von Ollama"
        except urllib.error.URLError as exc:
            self.last_llm_error = f"Ollama nicht erreichbar: {exc.reason}"
        except Exception as exc:
            self.last_llm_error = f"LLM-Fehler: {exc}"

        self.last_analysis_source = "fallback"
        return self._generate_rule_based_analysis(flights_with_kpis)
