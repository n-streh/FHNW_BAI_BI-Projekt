# Demo-Walkthrough (5 Minuten)

Kurzanleitung für Dozierende und Prüfende – FHNW Modul Business Intelligence.

---

## 1. Problemstellung (30 Sek.)

Eine Airline möchte **unterbelegte Flugrouten** identifizieren und **Umsatzpotenzial** durch gezielte Massnahmen erschliessen. Grundlage: reale Referenzdaten mit **54 Mio. Buchungen** (1.–7. Juni 2015).

---

## 2. Setup (1 Min.)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python setup_project.py
streamlit run app.py
```

**Optional (KI-Analyse):**

```powershell
ollama pull phi3
ollama serve
```

> Die App funktioniert auch **ohne** MySQL und Ollama – dank vorberechnetem Datenauszug (`flight_data.py`).

---

## 3. Architektur (1 Min.)

```
MySQL (54 Mio. Buchungen)
        │
        ▼  extract_data.py  (ETL)
flight_data.py  (lokaler Datenauszug)
        │
        ▼  agent.py  (KPIs, KI, Simulation)
app.py  (Streamlit-Dashboard)
        │
        ▼  optional: Ollama phi3  (lokales LLM)
```

**BI-Konzepte im Projekt:**

| Konzept | Umsetzung |
|---------|-----------|
| ETL / Staging | `extract_data.py` → `flight_data.py` |
| KPIs | Auslastung, Umsatz, Passagiere |
| Segmentierung | Flüge mit < 40 % Auslastung |
| Benchmarking | Vergleich mit Wochendurchschnitt (49,3 %) |
| Visual Analytics | Plotly-Charts im Dashboard |
| KI-gestützte Analyse | Ollama phi3 + regelbasierter Fallback |
| What-if-Simulation | Preissenkung −20 %, Ziel 85 % Auslastung |

---

## 4. Dashboard-Demo (2 Min.)

### Tab «Weltkarte» (Demo-Highlight)

1. Interaktive **Weltkarte** mit unterbelegten Routen
2. Farbe: rot = kritisch (&lt;25 %), orange = warnung, gelb = moderat
3. Hover: Flugnummer, Route, Auslastung, Umsatz

### Tab «Übersicht»

1. **Zeitraum wählen** (Sidebar): 1 Tag / 3 Tage / 1 Woche = sofort geladen ⚡
2. **KPI-Karten** und **Charts** (Auslastung, Umsatz, Benchmark)
3. Ab **14 Tagen**: Live-DB oder vorher `python extract_data.py` für schnelle Demo

### Tab «KI-Analyse»

1. Status in Sidebar prüfen (Ollama bereit?)
2. **«Analyse starten»** – erste Analyse dauert **1–3 Min.** (phi3 auf CPU)
3. Grünes Badge = LLM aktiv; bei Fallback siehe Fehlergrund

### Tab «Optimierung»

1. Expander **«Wie wird die Simulation berechnet?»** zeigt Formeln
2. Flug wählen → **«Simulation starten»**
3. Vorher/Nachher-Chart mit konkreten Rechenschritten

---

## 5. Diskussionspunkte (30 Sek.)

- Warum ETL statt Live-Query? (Performance bei 54 Mio. Zeilen)
- Wie werden KPIs definiert? (`agent.py` → `calculate_kpis`)
- Was passiert ohne LLM? (Robuster Fallback auf Regeln)
- Closed Loop: Daten → Insight → Entscheidung → Simulation

---

## Demo-Checkliste

- [ ] `python setup_project.py` zeigt «App startbereit»
- [ ] `streamlit run app.py` öffnet Dashboard im Browser
- [ ] Charts laden in Tab «Übersicht»
- [ ] KI-Analyse einmal vorab gestartet (LLM warm)
- [ ] Optimierung an Flug GE6237 demonstriert
