"""
Vorberechneter Datenauszug aus der Datenbank flughafendb_large.
Extrahiert am: 2026-06-21 14:13

Datenbank-Groesse: 462'553 Fluege, 54'304'619 Buchungen
Extraktion: 1 Hauptabfrage (Juni), Zeitraeume per Filter abgeleitet
"""

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

BEST_PERFORMING_FLIGHTS = [
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
        "id": 36721,
        "flightno": "SP7691",
        "route": "ANAKTUVUK PASS nach PUNTA RAISI",
        "departure_time": "2015-06-05 01:08:00",
        "capacity": 79,
        "passenger_count": 55,
        "load_factor": 69.62,
        "avg_price": 267.071636
    },
    {
        "id": 10500,
        "flightno": "JE9319",
        "route": "BAREILLY AB nach VAESTERAAS AB",
        "departure_time": "2015-06-02 04:03:00",
        "capacity": 78,
        "passenger_count": 54,
        "load_factor": 69.23,
        "avg_price": 232.023704
    }
]

WEEKLY_STATS = {
    "total_flights": 34811,
    "total_passengers": 4062889.0,
    "avg_passengers_per_flight": 116.7128,
    "avg_load_factor": 49.300322
}

PERIOD_PRESETS = {
    "1d": {
        "label": "1 Tag (1. Juni)",
        "start": "2015-06-01",
        "end": "2015-06-01",
        "preloaded": true,
        "slow_hint": null
    },
    "3d": {
        "label": "3 Tage (1.–3. Juni)",
        "start": "2015-06-01",
        "end": "2015-06-03",
        "preloaded": true,
        "slow_hint": null
    },
    "7d": {
        "label": "1 Woche (1.–7. Juni)",
        "start": "2015-06-01",
        "end": "2015-06-07",
        "preloaded": true,
        "slow_hint": null
    },
    "14d": {
        "label": "2 Wochen (1.–14. Juni)",
        "start": "2015-06-01",
        "end": "2015-06-14",
        "preloaded": true,
        "slow_hint": null
    },
    "30d": {
        "label": "1 Monat (Juni 2015)",
        "start": "2015-06-01",
        "end": "2015-06-30",
        "preloaded": true,
        "slow_hint": null
    }
}

PRELOADED_PERIOD_DATA = {
    "1d": {
        "underperforming": [
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
                "id": 545,
                "flightno": "BU2525",
                "route": "SANDSPIT nach GRAFENWOHR AAF",
                "departure_time": "2015-06-01 21:49:00",
                "capacity": 50,
                "passenger_count": 17,
                "ticket_price": 315.222941
            },
            {
                "id": 3044,
                "flightno": "NE7634",
                "route": "HAMILTON AERO nach SODDO",
                "departure_time": "2015-06-01 23:38:00",
                "capacity": 50,
                "passenger_count": 17,
                "ticket_price": 316.099412
            },
            {
                "id": 3055,
                "flightno": "NE9403",
                "route": "LAGRANGE-CALLAWAY nach WANNUKANDI",
                "departure_time": "2015-06-01 10:11:00",
                "capacity": 50,
                "passenger_count": 17,
                "ticket_price": 253.048235
            },
            {
                "id": 3167,
                "flightno": "OM5436",
                "route": "WARREN nach PHILADELPHIA MUN",
                "departure_time": "2015-06-01 13:33:00",
                "capacity": 50,
                "passenger_count": 17,
                "ticket_price": 176.083529
            },
            {
                "id": 71,
                "flightno": "AL3990",
                "route": "NUMMELA nach VIGAN",
                "departure_time": "2015-06-01 01:50:00",
                "capacity": 50,
                "passenger_count": 18,
                "ticket_price": 230.680556
            },
            {
                "id": 81,
                "flightno": "AL5630",
                "route": "IOANNINA nach SECUNDA",
                "departure_time": "2015-06-01 11:18:00",
                "capacity": 50,
                "passenger_count": 18,
                "ticket_price": 235.885556
            },
            {
                "id": 1923,
                "flightno": "IC3861",
                "route": "SALDANHA-VREDENBURG nach BLACK HILLS-ICE",
                "departure_time": "2015-06-01 04:16:00",
                "capacity": 50,
                "passenger_count": 18,
                "ticket_price": 171.781667
            },
            {
                "id": 2325,
                "flightno": "KA2254",
                "route": "VIBORG nach BANMAW",
                "departure_time": "2015-06-01 12:22:00",
                "capacity": 50,
                "passenger_count": 18,
                "ticket_price": 314.118333
            },
            {
                "id": 3761,
                "flightno": "SI7929",
                "route": "BAMBERG AAF nach IZUMO",
                "departure_time": "2015-06-01 03:41:00",
                "capacity": 50,
                "passenger_count": 18,
                "ticket_price": 286.385
            },
            {
                "id": 3987,
                "flightno": "SU1906",
                "route": "EL TEHUELCHE nach ROCLINCOURT",
                "departure_time": "2015-06-01 03:12:00",
                "capacity": 50,
                "passenger_count": 18,
                "ticket_price": 262.225556
            },
            {
                "id": 4157,
                "flightno": "TH1462",
                "route": "COLD BAY nach LEWISTON-NEZ PERCE CO",
                "departure_time": "2015-06-01 16:07:00",
                "capacity": 50,
                "passenger_count": 18,
                "ticket_price": 256.624444
            },
            {
                "id": 4399,
                "flightno": "UK4934",
                "route": "GUARANI INTL nach CHILLICOTHE MUN",
                "departure_time": "2015-06-01 18:39:00",
                "capacity": 50,
                "passenger_count": 18,
                "ticket_price": 258.101667
            },
            {
                "id": 4500,
                "flightno": "UZ1705",
                "route": "JUNIPER nach GOUNDAM",
                "departure_time": "2015-06-01 04:46:00",
                "capacity": 50,
                "passenger_count": 18,
                "ticket_price": 283.992222
            },
            {
                "id": 4696,
                "flightno": "WA7928",
                "route": "ZIA INTL nach MAUI A",
                "departure_time": "2015-06-01 07:48:00",
                "capacity": 50,
                "passenger_count": 18,
                "ticket_price": 291.308333
            }
        ],
        "best": [
            {
                "id": 1674,
                "flightno": "GI1545",
                "route": "WILLIAMS NOLF nach TRI-STATE STEUBEN CO",
                "departure_time": "2015-06-01 02:50:00",
                "capacity": 50,
                "passenger_count": 34,
                "load_factor": 68.0,
                "avg_price": 245.132941
            },
            {
                "id": 4264,
                "flightno": "TR8768",
                "route": "LIVERPOOL nach CONNAUGHT",
                "departure_time": "2015-06-01 19:31:00",
                "capacity": 50,
                "passenger_count": 34,
                "load_factor": 68.0,
                "avg_price": 261.734706
            },
            {
                "id": 2974,
                "flightno": "NA2931",
                "route": "SRI SATHYA SAI nach STORUMAN",
                "departure_time": "2015-06-01 15:36:00",
                "capacity": 78,
                "passenger_count": 52,
                "load_factor": 66.67,
                "avg_price": 234.313462
            },
            {
                "id": 4167,
                "flightno": "TH2631",
                "route": "ELK POINT nach NEWTOWNARDS",
                "departure_time": "2015-06-01 00:24:00",
                "capacity": 78,
                "passenger_count": 52,
                "load_factor": 66.67,
                "avg_price": 269.024615
            },
            {
                "id": 3369,
                "flightno": "PU1147",
                "route": "LA QUILLANE nach RED LODGE",
                "departure_time": "2015-06-01 03:17:00",
                "capacity": 95,
                "passenger_count": 63,
                "load_factor": 66.32,
                "avg_price": 264.608889
            },
            {
                "id": 565,
                "flightno": "BU5829",
                "route": "SEGELETZ nach ROSS CO",
                "departure_time": "2015-06-01 19:22:00",
                "capacity": 50,
                "passenger_count": 33,
                "load_factor": 66.0,
                "avg_price": 258.436364
            },
            {
                "id": 3003,
                "flightno": "NA8198",
                "route": "WILKES-BARRE-WYOMING VALLEY nach CRYSTAL",
                "departure_time": "2015-06-01 07:20:00",
                "capacity": 50,
                "passenger_count": 33,
                "load_factor": 66.0,
                "avg_price": 254.85303
            },
            {
                "id": 4604,
                "flightno": "VE3232",
                "route": "MALDEN MUN nach VANDENBERG",
                "departure_time": "2015-06-01 04:44:00",
                "capacity": 50,
                "passenger_count": 33,
                "load_factor": 66.0,
                "avg_price": 213.56303
            },
            {
                "id": 1937,
                "flightno": "IC5663",
                "route": "ALTURAS MUN nach TOMVALE",
                "departure_time": "2015-06-01 07:03:00",
                "capacity": 114,
                "passenger_count": 75,
                "load_factor": 65.79,
                "avg_price": 237.492933
            },
            {
                "id": 289,
                "flightno": "AZ5407",
                "route": "KANGERLUSSUAQ nach GODS RIVER",
                "departure_time": "2015-06-01 23:25:00",
                "capacity": 79,
                "passenger_count": 51,
                "load_factor": 64.56,
                "avg_price": 252.78451
            }
        ],
        "stats": {
            "total_flights": 4925,
            "total_passengers": 577356.0,
            "avg_passengers_per_flight": 117.2296,
            "avg_load_factor": 49.37786
        }
    },
    "3d": {
        "underperforming": [
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
                "id": 8694,
                "flightno": "BO9579",
                "route": "SARH nach MONT ROYAL",
                "departure_time": "2015-06-02 10:16:00",
                "capacity": 50,
                "passenger_count": 16,
                "ticket_price": 274.058125
            },
            {
                "id": 10994,
                "flightno": "MA3351",
                "route": "MERCED MUN/ MACREADY nach HERNING",
                "departure_time": "2015-06-02 22:24:00",
                "capacity": 50,
                "passenger_count": 16,
                "ticket_price": 215.17625
            },
            {
                "id": 11036,
                "flightno": "ME3207",
                "route": "MONTICHIARI nach DEHRADUN",
                "departure_time": "2015-06-02 14:06:00",
                "capacity": 50,
                "passenger_count": 16,
                "ticket_price": 300.0275
            },
            {
                "id": 11545,
                "flightno": "PE9936",
                "route": "BREMERTON NATL nach EL TEPUAL INTL",
                "departure_time": "2015-06-02 10:09:00",
                "capacity": 50,
                "passenger_count": 16,
                "ticket_price": 249.740625
            },
            {
                "id": 18518,
                "flightno": "IT8955",
                "route": "INYOKERN nach KERRVILLE MUN-SCHREINER",
                "departure_time": "2015-06-03 03:23:00",
                "capacity": 50,
                "passenger_count": 16,
                "ticket_price": 239.17125
            },
            {
                "id": 21014,
                "flightno": "VE9810",
                "route": "SELCUK-EFES nach SOROCABA",
                "departure_time": "2015-06-03 03:31:00",
                "capacity": 50,
                "passenger_count": 16,
                "ticket_price": 279.286875
            },
            {
                "id": 21043,
                "flightno": "VI6223",
                "route": "LUZIANIA nach CLAREMORE REGL",
                "departure_time": "2015-06-03 06:20:00",
                "capacity": 50,
                "passenger_count": 16,
                "ticket_price": 239.751875
            },
            {
                "id": 545,
                "flightno": "BU2525",
                "route": "SANDSPIT nach GRAFENWOHR AAF",
                "departure_time": "2015-06-01 21:49:00",
                "capacity": 50,
                "passenger_count": 17,
                "ticket_price": 315.222941
            },
            {
                "id": 3044,
                "flightno": "NE7634",
                "route": "HAMILTON AERO nach SODDO",
                "departure_time": "2015-06-01 23:38:00",
                "capacity": 50,
                "passenger_count": 17,
                "ticket_price": 316.099412
            }
        ],
        "best": [
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
                "id": 10500,
                "flightno": "JE9319",
                "route": "BAREILLY AB nach VAESTERAAS AB",
                "departure_time": "2015-06-02 04:03:00",
                "capacity": 78,
                "passenger_count": 54,
                "load_factor": 69.23,
                "avg_price": 232.023704
            },
            {
                "id": 1674,
                "flightno": "GI1545",
                "route": "WILLIAMS NOLF nach TRI-STATE STEUBEN CO",
                "departure_time": "2015-06-01 02:50:00",
                "capacity": 50,
                "passenger_count": 34,
                "load_factor": 68.0,
                "avg_price": 245.132941
            },
            {
                "id": 4264,
                "flightno": "TR8768",
                "route": "LIVERPOOL nach CONNAUGHT",
                "departure_time": "2015-06-01 19:31:00",
                "capacity": 50,
                "passenger_count": 34,
                "load_factor": 68.0,
                "avg_price": 261.734706
            },
            {
                "id": 11775,
                "flightno": "RE7920",
                "route": "ANGEL S ADAMI INTL nach KASHI",
                "departure_time": "2015-06-02 10:37:00",
                "capacity": 50,
                "passenger_count": 34,
                "load_factor": 68.0,
                "avg_price": 252.778529
            },
            {
                "id": 12497,
                "flightno": "TH8825",
                "route": "OTIS ANGB nach NAKHON SI THAMMARAT",
                "departure_time": "2015-06-02 05:37:00",
                "capacity": 50,
                "passenger_count": 34,
                "load_factor": 68.0,
                "avg_price": 273.292941
            },
            {
                "id": 18155,
                "flightno": "HA2474",
                "route": "RAYAK AB nach NEUMARKT/ OPF.",
                "departure_time": "2015-06-03 00:25:00",
                "capacity": 50,
                "passenger_count": 34,
                "load_factor": 68.0,
                "avg_price": 217.435882
            },
            {
                "id": 19784,
                "flightno": "PU7967",
                "route": "STEINBOURG nach TINGSRYD",
                "departure_time": "2015-06-03 02:32:00",
                "capacity": 79,
                "passenger_count": 53,
                "load_factor": 67.09,
                "avg_price": 268.997358
            }
        ],
        "stats": {
            "total_flights": 14957,
            "total_passengers": 1749415.0,
            "avg_passengers_per_flight": 116.963,
            "avg_load_factor": 49.309242
        }
    },
    "7d": {
        "underperforming": [
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
        ],
        "best": [
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
                "id": 36721,
                "flightno": "SP7691",
                "route": "ANAKTUVUK PASS nach PUNTA RAISI",
                "departure_time": "2015-06-05 01:08:00",
                "capacity": 79,
                "passenger_count": 55,
                "load_factor": 69.62,
                "avg_price": 267.071636
            },
            {
                "id": 10500,
                "flightno": "JE9319",
                "route": "BAREILLY AB nach VAESTERAAS AB",
                "departure_time": "2015-06-02 04:03:00",
                "capacity": 78,
                "passenger_count": 54,
                "load_factor": 69.23,
                "avg_price": 232.023704
            }
        ],
        "stats": {
            "total_flights": 34811,
            "total_passengers": 4062889.0,
            "avg_passengers_per_flight": 116.7128,
            "avg_load_factor": 49.300322
        }
    },
    "14d": {
        "underperforming": [
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
                "id": 69173,
                "flightno": "RU1227",
                "route": "KUMLINGE nach PALO ARCO",
                "departure_time": "2015-06-09 23:04:00",
                "capacity": 50,
                "passenger_count": 14,
                "ticket_price": 248.785714
            },
            {
                "id": 93787,
                "flightno": "RW8471",
                "route": "HELMS SEVIER CO nach KARLSBORG AB",
                "departure_time": "2015-06-12 16:39:00",
                "capacity": 50,
                "passenger_count": 14,
                "ticket_price": 173.536429
            },
            {
                "id": 100458,
                "flightno": "IV6685",
                "route": "KALMAR nach CAPAO BONITO",
                "departure_time": "2015-06-13 07:30:00",
                "capacity": 50,
                "passenger_count": 14,
                "ticket_price": 265.782143
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
            }
        ],
        "best": [
            {
                "id": 70009,
                "flightno": "UG4924",
                "route": "KANIAMA nach LUNEBURG",
                "departure_time": "2015-06-09 06:44:00",
                "capacity": 50,
                "passenger_count": 37,
                "load_factor": 74.0,
                "avg_price": 277.921622
            },
            {
                "id": 60451,
                "flightno": "NO3281",
                "route": "ALEXANDRIA nach ESQUEL",
                "departure_time": "2015-06-08 11:24:00",
                "capacity": 78,
                "passenger_count": 57,
                "load_factor": 73.08,
                "avg_price": 277.924561
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
                "id": 82610,
                "flightno": "CO3238",
                "route": "HORICE nach ARISTOTELIS",
                "departure_time": "2015-06-11 05:34:00",
                "capacity": 50,
                "passenger_count": 36,
                "load_factor": 72.0,
                "avg_price": 264.268611
            },
            {
                "id": 109835,
                "flightno": "PH6846",
                "route": "VICTORIA FALLS nach SEBBA",
                "departure_time": "2015-06-14 12:40:00",
                "capacity": 78,
                "passenger_count": 56,
                "load_factor": 71.79,
                "avg_price": 234.665536
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
                "id": 36083,
                "flightno": "PE6957",
                "route": "BALSAS nach PRESIDENTE PERON",
                "departure_time": "2015-06-05 12:51:00",
                "capacity": 50,
                "passenger_count": 35,
                "load_factor": 70.0,
                "avg_price": 255.143429
            }
        ],
        "stats": {
            "total_flights": 69622,
            "total_passengers": 8163239.0,
            "avg_passengers_per_flight": 117.2509,
            "avg_load_factor": 49.301327
        }
    },
    "30d": {
        "underperforming": [
            {
                "id": 173807,
                "flightno": "HA2926",
                "route": "BRUSSELS SOUTH nach LILONGWE INTL",
                "departure_time": "2015-06-22 23:20:00",
                "capacity": 50,
                "passenger_count": 11,
                "ticket_price": 267.908182
            },
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
                "id": 142800,
                "flightno": "RU2289",
                "route": "FLAMINGO nach OSHOGBO",
                "departure_time": "2015-06-18 08:26:00",
                "capacity": 50,
                "passenger_count": 12,
                "ticket_price": 250.3
            },
            {
                "id": 233927,
                "flightno": "VA8874",
                "route": "NETOOK nach PAMPA GRANDE",
                "departure_time": "2015-06-29 04:08:00",
                "capacity": 50,
                "passenger_count": 12,
                "ticket_price": 181.6875
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
                "id": 176702,
                "flightno": "WA6522",
                "route": "ELKHART MUN nach PLYMOUTH",
                "departure_time": "2015-06-22 08:40:00",
                "capacity": 50,
                "passenger_count": 13,
                "ticket_price": 148.746923
            },
            {
                "id": 230817,
                "flightno": "FI1380",
                "route": "LUBERO nach AYERS ROCK (CONNELLAN)",
                "departure_time": "2015-06-29 05:53:00",
                "capacity": 50,
                "passenger_count": 13,
                "ticket_price": 338.399231
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
                "id": 69173,
                "flightno": "RU1227",
                "route": "KUMLINGE nach PALO ARCO",
                "departure_time": "2015-06-09 23:04:00",
                "capacity": 50,
                "passenger_count": 14,
                "ticket_price": 248.785714
            },
            {
                "id": 93787,
                "flightno": "RW8471",
                "route": "HELMS SEVIER CO nach KARLSBORG AB",
                "departure_time": "2015-06-12 16:39:00",
                "capacity": 50,
                "passenger_count": 14,
                "ticket_price": 173.536429
            },
            {
                "id": 100458,
                "flightno": "IV6685",
                "route": "KALMAR nach CAPAO BONITO",
                "departure_time": "2015-06-13 07:30:00",
                "capacity": 50,
                "passenger_count": 14,
                "ticket_price": 265.782143
            },
            {
                "id": 131334,
                "flightno": "AZ1358",
                "route": "HENRY CO nach ALAMOGORDO-WHITE SANDS REGL",
                "departure_time": "2015-06-17 16:35:00",
                "capacity": 50,
                "passenger_count": 14,
                "ticket_price": 214.706429
            }
        ],
        "best": [
            {
                "id": 184856,
                "flightno": "UZ8405",
                "route": "BENI-DIBELE nach MARYS HARBOUR",
                "departure_time": "2015-06-23 08:57:00",
                "capacity": 50,
                "passenger_count": 53,
                "load_factor": 106.0,
                "avg_price": 247.075472
            },
            {
                "id": 198439,
                "flightno": "HO9631",
                "route": "ALEXANDRIA nach KHOST",
                "departure_time": "2015-06-25 18:21:00",
                "capacity": 50,
                "passenger_count": 52,
                "load_factor": 104.0,
                "avg_price": 252.601731
            },
            {
                "id": 70009,
                "flightno": "UG4924",
                "route": "KANIAMA nach LUNEBURG",
                "departure_time": "2015-06-09 06:44:00",
                "capacity": 50,
                "passenger_count": 37,
                "load_factor": 74.0,
                "avg_price": 277.921622
            },
            {
                "id": 172223,
                "flightno": "AR7799",
                "route": "MPAKA nach CANGAPARA",
                "departure_time": "2015-06-22 06:06:00",
                "capacity": 50,
                "passenger_count": 37,
                "load_factor": 74.0,
                "avg_price": 273.237027
            },
            {
                "id": 60451,
                "flightno": "NO3281",
                "route": "ALEXANDRIA nach ESQUEL",
                "departure_time": "2015-06-08 11:24:00",
                "capacity": 78,
                "passenger_count": 57,
                "load_factor": 73.08,
                "avg_price": 277.924561
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
                "id": 82610,
                "flightno": "CO3238",
                "route": "HORICE nach ARISTOTELIS",
                "departure_time": "2015-06-11 05:34:00",
                "capacity": 50,
                "passenger_count": 36,
                "load_factor": 72.0,
                "avg_price": 264.268611
            },
            {
                "id": 115332,
                "flightno": "CE7243",
                "route": "SAARLOUIS-DUREN nach REVELSTOKE",
                "departure_time": "2015-06-15 08:30:00",
                "capacity": 50,
                "passenger_count": 36,
                "load_factor": 72.0,
                "avg_price": 247.695
            }
        ],
        "stats": {
            "total_flights": 149254,
            "total_passengers": 17540333.0,
            "avg_passengers_per_flight": 117.52,
            "avg_load_factor": 49.281569
        }
    }
}

EXTENDED_PERIOD_DATA = {}


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
