"""
Vorberechneter Datenauszug aus der Datenbank flughafendb_large.
Extrahiert am: 2026-05-25 11:43

Datenbank-Groesse: 462'553 Fluege, 54'304'619 Buchungen
Zeitraum: 1. bis 7. Juni 2015

Dieser Datenauszug vermeidet die langsamen Queries ueber die 54-Millionen-Buchungstabelle
und ermoeglicht einen sofortigen Start der Streamlit-App.
"""

# Top 15 unterbelegte Fluege (Auslastung < 40%)
UNDERPERFORMING_FLIGHTS = [
    {
        "id": 34391,
        "flightno": "GE6237",
        "route": "NOVO HORIZONTE nach COL FRANCISCO SECADA VIGNETTA",
        "departure_time": "2015-06-05 18:21:00",
        "capacity": 50,
        "passenger_count": 12,
        "ticket_price": 266.745
    },
    {
        "id": 35415,
        "flightno": "LE7942",
        "route": "BROADUS nach ROCKY MOUNTAIN HOUSE",
        "departure_time": "2015-06-05 15:40:00",
        "capacity": 50,
        "passenger_count": 12,
        "ticket_price": 197.9225
    },
    {
        "id": 40999,
        "flightno": "AF9434",
        "route": "ENOGGERA nach NEW TEMPE",
        "departure_time": "2015-06-06 07:13:00",
        "capacity": 50,
        "passenger_count": 12,
        "ticket_price": 222.574167
    },
    {
        "id": 25280,
        "flightno": "CO4307",
        "route": "HAVRE ST-PIERRE nach WAREHOUSE 59-E",
        "departure_time": "2015-06-04 16:03:00",
        "capacity": 50,
        "passenger_count": 13,
        "ticket_price": 172.763846
    },
    {
        "id": 44022,
        "flightno": "NI6638",
        "route": "GATWICK nach POCONE",
        "departure_time": "2015-06-06 06:16:00",
        "capacity": 50,
        "passenger_count": 13,
        "ticket_price": 221.927692
    },
    {
        "id": 50487,
        "flightno": "ES5135",
        "route": "SHAMATTAWA nach LAKE PLACID",
        "departure_time": "2015-06-07 18:38:00",
        "capacity": 50,
        "passenger_count": 14,
        "ticket_price": 242.84
    },
    {
        "id": 3612,
        "flightno": "RW1385",
        "route": "BOQUIRA nach SAN PABLO",
        "departure_time": "2015-06-01 16:40:00",
        "capacity": 50,
        "passenger_count": 15,
        "ticket_price": 246.692667
    },
    {
        "id": 8539,
        "flightno": "BA6650",
        "route": "NIEDEROBLARN nach KARMOY",
        "departure_time": "2015-06-02 00:14:00",
        "capacity": 50,
        "passenger_count": 15,
        "ticket_price": 198.392
    },
    {
        "id": 8754,
        "flightno": "BU1289",
        "route": "SELIBABI nach SOUTHERN ILLINOIS",
        "departure_time": "2015-06-02 01:19:00",
        "capacity": 50,
        "passenger_count": 15,
        "ticket_price": 354.371333
    },
    {
        "id": 16397,
        "flightno": "AF2227",
        "route": "MARISCAL ANTONIO JOSE DE SUCRE nach BAU",
        "departure_time": "2015-06-03 05:00:00",
        "capacity": 50,
        "passenger_count": 15,
        "ticket_price": 242.586
    },
    {
        "id": 17306,
        "flightno": "DA1183",
        "route": "HERMISTON MUN nach GWAKA",
        "departure_time": "2015-06-03 17:11:00",
        "capacity": 50,
        "passenger_count": 15,
        "ticket_price": 186.422
    },
    {
        "id": 20494,
        "flightno": "TA5309",
        "route": "ROTHENBURG/ GORLITZ nach LE MAZET DE ROMANIN",
        "departure_time": "2015-06-03 23:00:00",
        "capacity": 50,
        "passenger_count": 15,
        "ticket_price": 233.685333
    },
    {
        "id": 33493,
        "flightno": "CH9695",
        "route": "MOORELAND MUN nach MONKOTO",
        "departure_time": "2015-06-05 15:20:00",
        "capacity": 50,
        "passenger_count": 15,
        "ticket_price": 328.204667
    },
    {
        "id": 41678,
        "flightno": "CR1655",
        "route": "CAMPO GRANDE INTL nach TROMBETAS",
        "departure_time": "2015-06-06 20:37:00",
        "capacity": 50,
        "passenger_count": 15,
        "ticket_price": 287.25
    },
    {
        "id": 44811,
        "flightno": "SP1198",
        "route": "SEITENSTETTEN nach POBIEDNIK WIELKI",
        "departure_time": "2015-06-06 07:35:00",
        "capacity": 50,
        "passenger_count": 15,
        "ticket_price": 243.628667
    }
]

# Top 10 bestausgelastete Fluege (zum Vergleich fuer die Analyse)
BEST_PERFORMING_FLIGHTS = [
    {
        "id": 49821,
        "flightno": "CH4035",
        "route": "CLINTON CO nach CASTRO ALVES",
        "departure_time": "2015-06-07 08:26:00",
        "capacity": 50,
        "passenger_count": 36,
        "load_factor": 72.0,
        "avg_price": 242.654722
    },
    {
        "id": 17561,
        "flightno": "EL5250",
        "route": "COSTA RICA nach CRESTON MUN",
        "departure_time": "2015-06-03 04:36:00",
        "capacity": 50,
        "passenger_count": 36,
        "load_factor": 72.0,
        "avg_price": 259.456944
    },
    {
        "id": 37550,
        "flightno": "WA8980",
        "route": "USIMINAS nach COMILLA",
        "departure_time": "2015-06-05 21:28:00",
        "capacity": 50,
        "passenger_count": 36,
        "load_factor": 72.0,
        "avg_price": 218.774722
    },
    {
        "id": 36083,
        "flightno": "PE6957",
        "route": "BALSAS nach PRESIDENTE PERON",
        "departure_time": "2015-06-05 12:51:00",
        "capacity": 50,
        "passenger_count": 35,
        "load_factor": 70.0,
        "avg_price": 255.143429
    },
    {
        "id": 36688,
        "flightno": "SP1065",
        "route": "LODWAR nach MALINDI",
        "departure_time": "2015-06-05 15:03:00",
        "capacity": 50,
        "passenger_count": 35,
        "load_factor": 70.0,
        "avg_price": 263.715143
    },
    {
        "id": 19280,
        "flightno": "MO7640",
        "route": "KUTAHYA AB nach LUBBOCK INTL",
        "departure_time": "2015-06-03 01:49:00",
        "capacity": 50,
        "passenger_count": 35,
        "load_factor": 70.0,
        "avg_price": 229.470857
    },
    {
        "id": 44029,
        "flightno": "NI8028",
        "route": "LUKOU nach BANKSTOWN",
        "departure_time": "2015-06-06 04:17:00",
        "capacity": 50,
        "passenger_count": 35,
        "load_factor": 70.0,
        "avg_price": 232.374286
    },
    {
        "id": 9090,
        "flightno": "CY3975",
        "route": "WASECA MUN nach HENDRIK VAN ECK",
        "departure_time": "2015-06-02 08:21:00",
        "capacity": 50,
        "passenger_count": 35,
        "load_factor": 70.0,
        "avg_price": 259.108286
    },
    {
        "id": 36721,
        "flightno": "SP7691",
        "route": "ANAKTUVUK PASS nach PUNTA RAISI",
        "departure_time": "2015-06-05 01:08:00",
        "capacity": 79,
        "passenger_count": 55,
        "load_factor": 69.6,
        "avg_price": 267.071636
    },
    {
        "id": 10500,
        "flightno": "JE9319",
        "route": "BAREILLY AB nach VAESTERAAS AB",
        "departure_time": "2015-06-02 04:03:00",
        "capacity": 78,
        "passenger_count": 54,
        "load_factor": 69.2,
        "avg_price": 232.023704
    }
]

# Wochenstatistik (Gesamtueberblick)
WEEKLY_STATS = {
    "total_flights": 34811,
    "total_passengers": 4062889.0,
    "avg_passengers_per_flight": 116.7128,
    "avg_load_factor": 49.300309005
}

def get_underperforming_flights(limit=5):
    """Gibt die am schlechtesten ausgelasteten Fluege zurueck."""
    return UNDERPERFORMING_FLIGHTS[:limit]

def get_best_performing_flights(limit=5):
    """Gibt die am besten ausgelasteten Fluege zurueck."""
    return BEST_PERFORMING_FLIGHTS[:limit]

def get_weekly_stats():
    """Gibt die Wochenstatistik zurueck."""
    return WEEKLY_STATS


# --- Zeitraum-Filter (vorberechnete Presets) ---

PERIOD_PRESETS = {
    "1d": {
        "label": "1 Tag (1. Juni)",
        "start": "2015-06-01",
        "end": "2015-06-01",
        "preloaded": True,
        "slow_hint": None,
    },
    "3d": {
        "label": "3 Tage (1.–3. Juni)",
        "start": "2015-06-01",
        "end": "2015-06-03",
        "preloaded": True,
        "slow_hint": None,
    },
    "7d": {
        "label": "1 Woche (1.–7. Juni)",
        "start": "2015-06-01",
        "end": "2015-06-07",
        "preloaded": True,
        "slow_hint": None,
    },
    "14d": {
        "label": "2 Wochen (1.–14. Juni)",
        "start": "2015-06-01",
        "end": "2015-06-14",
        "preloaded": False,
        "slow_hint": "Live-Abfrage: ca. 1–3 Minuten",
    },
    "30d": {
        "label": "1 Monat (Juni 2015)",
        "start": "2015-06-01",
        "end": "2015-06-30",
        "preloaded": False,
        "slow_hint": "Live-Abfrage: kann 3–5 Minuten dauern",
    },
}


def _filter_by_date(flights, start, end):
    return [f for f in flights if start <= f["departure_time"][:10] <= end]


def _scale_stats(stats, factor):
    return {
        "total_flights": max(int(stats["total_flights"] * factor), 1),
        "total_passengers": round(stats["total_passengers"] * factor, 1),
        "avg_passengers_per_flight": stats["avg_passengers_per_flight"],
        "avg_load_factor": stats["avg_load_factor"],
    }


def _build_period_data():
    """Baut vorberechnete Zeitraeume aus dem Wochen-Extrakt (1d/3d/7d)."""
    configs = [
        ("1d", "2015-06-01", "2015-06-01", 1 / 7),
        ("3d", "2015-06-01", "2015-06-03", 3 / 7),
        ("7d", "2015-06-01", "2015-06-07", 1.0),
    ]
    data = {}
    for key, start, end, factor in configs:
        under = _filter_by_date(UNDERPERFORMING_FLIGHTS, start, end)
        best = _filter_by_date(BEST_PERFORMING_FLIGHTS, start, end)
        data[key] = {
            "underperforming": under,
            "best": best,
            "stats": _scale_stats(WEEKLY_STATS, factor),
        }
    return data


# Erweiterte Presets (14d/30d) – per extract_data.py befuellbar
EXTENDED_PERIOD_DATA = {}

PRELOADED_PERIOD_DATA = _build_period_data()


def get_period_presets():
    return PERIOD_PRESETS


def is_period_preloaded(period_key):
    preset = PERIOD_PRESETS.get(period_key, {})
    if preset.get("preloaded"):
        return True
    return period_key in EXTENDED_PERIOD_DATA


def get_period_data(period_key):
    if period_key in EXTENDED_PERIOD_DATA:
        return EXTENDED_PERIOD_DATA[period_key]
    return PRELOADED_PERIOD_DATA.get(period_key)
