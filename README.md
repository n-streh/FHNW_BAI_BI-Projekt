# FHNW BAI BI-Projekt – Flughafen Analyseplattform

Eine Airline möchte **unterbelegte Flugrouten** identifizieren und **Umsatzpotenzial** durch gezielte Massnahmen erschliessen. Dieses Projekt liefert dafür eine interaktive BI-Analyseplattform auf Basis realer Referenzdaten mit **54 Millionen Buchungen** (Juni 2015).

Die Anwendung besteht aus einem **Streamlit-Dashboard** (`app.py`), einer **Analyselogik** mit KPIs, KI und Simulation (`agent.py`) sowie einem **vorberechneten Datenauszug** (`flight_data.py`), der den Start beschleunigt und eine reproduzierbare Demo ohne Live-Queries auf dem grossen DB-Server ermöglicht.

---

## Funktionen

| Bereich | Beschreibung |
|---------|--------------|
| **KPI-Dashboard** | Auslastung, Umsatz und Passagierzahlen für unterbelegte Flüge (< 40 %) |
| **Weltkarte** | Interaktive Routenvisualisierung mit Farbcodierung nach Auslastung |
| **Benchmarking** | Vergleich einzelner Flüge mit dem Zeitraum-Durchschnitt |
| **KI-Analyse** | Lokales LLM (Ollama phi3) mit regelbasiertem Fallback |
| **What-if-Simulation** | Preissenkung −20 %, Ziel 85 % Auslastung, konkrete Rechenschritte |
| **Zeitraum-Filter** | 1 Tag bis 1 Monat – vorberechnete Perioden laden sofort |

### BI-Konzepte im Projekt

| Konzept | Umsetzung |
|---------|-----------|
| ETL / Staging | `extract_data.py` → `flight_data.py` |
| KPIs | Auslastung, Umsatz, Passagiere (`agent.py` → `calculate_kpis`) |
| Segmentierung | Flüge mit < 40 % Auslastung |
| Benchmarking | Vergleich mit Wochendurchschnitt |
| Visual Analytics | Plotly-Charts und interaktive Weltkarte |
| KI-gestützte Analyse | Ollama phi3 + regelbasierter Fallback |
| What-if-Simulation | Nachfragemodell mit Preis- und Auslastungsziel |

---

## Architektur

```
MySQL (54 Mio. Buchungen)
        │
        ▼  extract_data.py  (ETL)
flight_data.py  (lokaler Datenauszug)
        │
        ▼  agent.py  (KPIs, KI, Simulation)
app.py  (Streamlit-Dashboard)
        │
        ▼  Ollama phi3  (lokales LLM)
```

**Datenfluss:** Beim Start nutzt `agent.py` zuerst den lokalen Datenauszug in `flight_data.py`. Für Zeiträume ab 14 Tagen oder zum Aktualisieren der Geo-Daten kann optional live gegen MySQL abgefragt werden. Die KI-Analyse läuft über die lokale Ollama-API.

---

## Anforderungen

- **Python** 3.10 oder neuer
- **Ollama** mit Modell **phi3** (für die KI-Analyse)
- **MySQL/MariaDB** mit Datenbank `flughafendb_large` (optional für Standard-Demo; erforderlich für Live-Abfragen und Datenauszug-Update)

---

## Installation & Setup

### 1. Repository vorbereiten

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 2. Ollama einrichten

Die KI-Analyse im Tab «KI-Analyse» verwendet die lokale Ollama-API unter `http://localhost:11434` mit dem Modell **phi3**.

1. Ollama installieren: [https://ollama.com](https://ollama.com)
2. Modell laden:

```powershell
ollama pull phi3
```

3. Ollama starten (läuft unter Windows meist automatisch im Hintergrund):

```powershell
ollama serve
```

> **Hinweis:** Die erste KI-Analyse kann auf CPU **1–3 Minuten** dauern. Im Sidebar wird der Ollama-Status angezeigt. Ist Ollama nicht erreichbar, greift die App auf eine regelbasierte Analyse zurück – für die volle Funktionalität ist Ollama jedoch Teil des Setups.

### 3. Projekt-Check ausführen

```powershell
python setup_project.py
```

Das Skript prüft Python-Version, Pakete, Ollama und optional die Datenbankverbindung. Ziel: Meldung **«App startbereit»** oder **«Alle Checks bestanden»**.

### 4. Anwendung starten

```powershell
streamlit run app.py
```

Das Dashboard öffnet sich im Browser unter `http://localhost:8501`.

---

## Handhabung

### Sidebar

- **Beobachtungszeitraum** wählen (1 Tag / 3 Tage / 1 Woche / 2 Wochen / 1 Monat)
- Perioden mit ⚡ sind vorberechnet und laden sofort (Weiterentwicklung mit manueller Kalendersortierung wurde in Demo bewusst nicht umgesetzt)
- **Daten neu laden** setzt den Cache zurück
- **KI-Status** zeigt, ob Ollama bereit ist

### Tab «Weltkarte»

Interaktive Weltkarte mit unterbelegten Routen und den Top-5 bestausgelasteten Flügen als Referenz.

- **Rot** = kritisch (< 25 % Auslastung)
- **Orange** = Warnung (25–30 %)
- **Gelb** = moderat (30–40 %)
- **Grün gestrichelt** = Top-Routen im Zeitraum

Hover zeigt Flugnummer, Route, Auslastung und Umsatz. Im Expander «Routen-Details» stehen tabellarische Details.

### Tab «Übersicht»

KPI-Karten (durchschnittliche Auslastung, Gesamtumsatz, Passagiere, optimierte Flüge) sowie drei Charts:

1. Auslastung unterbelegter Flüge (mit Schwellenlinie 40 % und Zeitraum-Durchschnitt)
2. Umsatz pro Flug
3. Benchmark-Vergleich mit Zeitraum-Durchschnitt

Darunter eine Tabelle aller unterbelegten Flüge im gewählten Zeitraum.

### Tab «KI-Analyse»

1. Ollama-Status in der Sidebar prüfen
2. **«Analyse starten»** klicken – die Analyse blockiert nicht den Seitenaufbau
3. Grünes Badge = LLM aktiv (Ollama phi3); blaues Info-Badge = regelbasierter Fallback

Die KI bewertet die unterbelegten Routen und schlägt konkrete Massnahmen vor.

### Tab «Optimierung»

What-if-Simulation für einzelne Flüge:

1. Flug aus der Liste wählen
2. Expander **«Wie wird die Simulation berechnet?»** zeigt Parameter und Formeln
3. **Vorher/Nachher-Chart** zeigt Auslastung, Umsatz und Passagiere (Vorschau vor, bestätigt nach Simulation)
4. **«Simulation starten»** übernimmt die Werte in die Analyse
5. **«Zurücksetzen»** stellt den Ausgangszustand wieder her

**Modell:** Durchschnittspreis −20 %, simulierte Nachfrage bis 85 % Auslastung (mind. +10 Passagiere). Keine echten DB-Schreibungen.

---

## Lokaler Datenauszug

Um Live-Queries über 54 Millionen Buchungen zu vermeiden, enthält `flight_data.py` bereits extrahierte, bereinigte Flugdaten:

- Zeiträume **1–7 Tage** laden **sofort** (vorberechnet)
- Zeiträume **14–30 Tage**: nach `extract_data.py` sofort; sonst Live-MySQL (1–5 Min.)

| Zeitraum | Ladezeit | Quelle |
|----------|----------|--------|
| 1–7 Tage | Sofort | `flight_data.py` |
| 14–30 Tage | Nach Extrakt: sofort; sonst Live-DB | Extrakt oder MySQL |

### Datenauszug aktualisieren

```powershell
python extract_data.py
```

Damit wird `flight_data.py` neu erstellt. Eine Hauptabfrage für den gesamten Juni liefert alle Perioden; kürzere Zeiträume werden per Filter abgeleitet. Fortschritt wird im Terminal angezeigt.

---

## Datenbank (optional)

Für die Standard-Demo reicht der vorberechnete Datenauszug – **MySQL ist nicht zwingend nötig**. Für Live-Abfragen (Zeiträume ab 14 Tagen ohne Extrakt) oder zum Neuerzeugen des Datenauszugs wird eine Verbindung zur Referenzdatenbank benötigt.

Zugangsdaten in `agent.py`, `db_setup.py` und `extract_data.py` anpassen:

| Variable | Standardwert |
|----------|--------------|
| `DB_HOST` | `localhost` |
| `DB_USER` | `root` |
| `DB_PASSWORD` | `Startup.6` |
| `DB_NAME` | `flughafendb_large` |

Erforderliche Tabellen: `flight`, `booking`, `airport`, `airplane` (plus `airport_geo` für die Weltkarte).

---

## Demo-Checkliste

Vor einer Präsentation oder Abgabe:

- [ ] `python setup_project.py` zeigt «App startbereit»
- [ ] `ollama pull phi3` ausgeführt, Ollama läuft
- [ ] `streamlit run app.py` öffnet Dashboard im Browser
- [ ] Charts laden in Tab «Übersicht»
- [ ] Weltkarte zeigt Routen in Tab «Weltkarte»
- [ ] KI-Analyse einmal vorab gestartet (LLM «warm»)
- [ ] Optimierung an einem Flug demonstriert (z. B. GE6237)

---

## Projektstruktur

| Datei | Rolle |
|-------|-------|
| `app.py` | Streamlit-Dashboard |
| `agent.py` | KPIs, KI-Analyse, Simulation |
| `flight_data.py` | Vorberechneter Datenauszug |
| `extract_data.py` | ETL-Skript für Datenauszug |
| `route_map.py` | Weltkarten-Visualisierung |
| `setup_project.py` | Initialisierungscheck |
| `db_setup.py` | Datenbank-Setup-Hilfe |

---

## Lizenz

Siehe [LICENSE](LICENSE).
