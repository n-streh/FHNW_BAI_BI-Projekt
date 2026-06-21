# FHNW BAI BI-Projekt

Dieses Projekt ist eine Analyseplattform zur Bewertung von Flugrouten-Auslastung und Umsatzpotenzial. Es besteht aus einem Streamlit-Dashboard (`app.py`), einem Agenten für die Analyselogik (`agent.py`) und einem optionalen Datenextrakt, der lokal im Projekt gespeichert ist, um den Start und die Ausführung zu beschleunigen.

## Besonderheit: Lokaler Datenextrakt

Um ein sehr langsames Live-Query über die 54 Millionen Buchungen der Referenzdatenbank zu vermeiden, verwendet dieses Projekt einen vorberechneten Datenauszug:

- `flight_data.py` enthält bereits extrahierte, bereinigte Flugdaten für die Analyse.
- `agent.py` versucht beim Start zuerst, diesen lokalen Datenextrakt zu nutzen.
- Dadurch startet die App deutlich schneller und ist unabhängig von schnellen Live-Queries auf dem großen DB-Server.

Wenn Sie das Projekt lokal mit einer eigenen Datenbankverbindung betreiben möchten, können Sie trotzdem auf die Live-Daten zugreifen. In diesem Fall müssen Sie die Zugangsdaten an mehreren Stellen anpassen.

## Anforderungen

- Python 3.10 oder neuer
- MySQL/MariaDB-Server mit der Datenbank `flughafendb_large`
- Lokales Ollama, falls die LLM-Analyse aktiv genutzt werden soll

## Installation

1. Virtuelle Umgebung erstellen (empfohlen):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Abhängigkeiten installieren:

```powershell
python -m pip install -r requirements.txt
```

3. Projekt-Check ausführen:

```powershell
python setup_project.py
```

## Projekt starten

Starten Sie das Streamlit-Dashboard:

```powershell
streamlit run app.py
```

## Datenbankzugang lokal anpassen

Wenn Sie statt des gespeicherten Datenauszugs direkt auf Ihre lokale MySQL-Datenbank zugreifen möchten, müssen Sie die Zugangsdaten in folgenden Dateien anpassen:

- `agent.py`
- `db_setup.py`
- `extract_data.py`

In allen drei Dateien sind die Variablen:

- `DB_HOST`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`

zu erwarten. Standardwerte im Projekt sind:

- `DB_HOST = "localhost"`
- `DB_USER = "root"`
- `DB_PASSWORD = "Startup.6"`
- `DB_NAME = "flughafendb_large"`

Stellen Sie sicher, dass Ihr MySQL-Benutzer die Tabellen hat:

- `flight`
- `booking`
- `airport`
- `airplane`

## Ollama

Die KI-Analyse in `agent.py` verwendet die lokale Ollama-API unter `http://localhost:11434` mit dem Modell **phi3**.

1. Ollama installieren: [https://ollama.com](https://ollama.com)
2. Modell laden:

```powershell
ollama pull phi3
```

3. Ollama starten (läuft meist automatisch im Hintergrund):

```powershell
ollama serve
```

- Wenn Ollama nicht verfügbar ist, fällt das Projekt auf eine **regelbasierte Analyse** zurück.

## Demo-Walkthrough

Eine 5-Minuten-Anleitung für Dozierende finden Sie in [`DEMO.md`](DEMO.md).

## Datenextrakt aktualisieren

Falls Sie den lokalen Datenauszug neu erzeugen möchten (inkl. Zeiträume 14d/30d):

```powershell
python extract_data.py
```

Damit wird `flight_data.py` neu erstellt. **Optimierung:** Eine Hauptabfrage für den gesamten Juni; kürzere Zeiträume werden daraus per Filter abgeleitet (statt 5× separate DB-Queries). Fortschritt wird im Terminal angezeigt.

### Zeitraum-Filter

| Zeitraum | Ladezeit | Quelle |
|----------|----------|--------|
| 1–7 Tage | Sofort | Vorberechnet in `flight_data.py` |
| 14–30 Tage | Nach `extract_data.py`: sofort; sonst Live-DB (1–5 Min.) | Extrakt oder MySQL |

## Hinweise für die Abgabe

- Der lokale Datenextrakt ist bewusst Teil des Projekts, damit die Anwendung schnell und reproduzierbar läuft.
- Die Live-Datenbankverbindung ist optional, aber dann müssen Sie die Zugangsdaten in `agent.py`, `db_setup.py` und `extract_data.py` anpassen.
