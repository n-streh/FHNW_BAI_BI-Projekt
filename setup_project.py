import json
import shutil
import sys
import urllib.request
import urllib.error

import mysql.connector

REQUIRED_PACKAGES = [
    ("streamlit", "streamlit"),
    ("pandas", "pandas"),
    ("mysql-connector-python", "mysql.connector"),
    ("plotly", "plotly"),
]

OLLAMA_URL = "http://localhost:11434/api/generate"


def check_python_version(min_major=3, min_minor=10):
    version_info = sys.version_info
    ok = (version_info.major, version_info.minor) >= (min_major, min_minor)
    return ok, f"{version_info.major}.{version_info.minor}.{version_info.micro}"


def check_packages():
    results = []
    for package_name, import_name in REQUIRED_PACKAGES:
        try:
            __import__(import_name)
            results.append((package_name, True, "OK"))
        except Exception as exc:
            results.append((package_name, False, str(exc)))
    return results


def check_ollama_cli():
    path = shutil.which("ollama")
    if path:
        return True, path
    return False, None


def check_ollama_api():
    try:
        request = urllib.request.Request(
            OLLAMA_URL,
            data=json.dumps({"model": "phi3", "prompt": "Ping", "stream": False}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            if response.status == 200:
                return True, "Ollama API erreichbar"
            return False, f"Unerwarteter HTTP-Status {response.status}"
    except urllib.error.URLError as exc:
        return False, str(exc)
    except Exception as exc:
        return False, str(exc)


def check_database():
    host = "localhost"
    user = "root"
    password = "Startup.6"
    database = "flughafendb_large"
    required_tables = ["flight", "booking", "airport", "airplane"]

    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            connection_timeout=5,
        )
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = {row[0] for row in cursor.fetchall()}
        missing = [t for t in required_tables if t not in tables]
        cursor.close()
        conn.close()
        if missing:
            return False, f"Datenbank verbunden, aber fehlende Tabellen: {', '.join(missing)}"
        return True, f"Datenbank '{database}' erreichbar und Tabellen gefunden."
    except Exception as exc:
        return False, str(exc)


def main():
    print("Projekt-Initialisierungscheck für FHNW_BAI_BI-Projekt\n")

    python_ok, python_version = check_python_version()
    print(f"Python-Version: {python_version}")
    if not python_ok:
        print("  ⚠️ Benötigt wird mindestens Python 3.10.")

    print("\nAbhängigkeiten prüfen:")
    package_results = check_packages()
    for package_name, available, message in package_results:
        status = "OK" if available else "FEHLT"
        print(f"  {package_name}: {status} ({message})")

    print("\nOllama-CLI prüfen:")
    cli_ok, cli_path = check_ollama_cli()
    if cli_ok:
        print(f"  ollama CLI gefunden: {cli_path}")
    else:
        print("  ⚠️ ollama CLI nicht gefunden. Bitte installieren Sie Ollama und stellen Sie sicher, dass der Befehl 'ollama' im PATH verfügbar ist.")

    print("\nOllama-Service prüfen:")
    api_ok, api_message = check_ollama_api()
    if api_ok:
        print(f"  OK: {api_message}")
    else:
        print(f"  ⚠️ Ollama-API nicht erreichbar: {api_message}")
        print("    Stellen Sie sicher, dass Ollama lokal läuft.")
        print("    Modell laden: ollama pull phi3")
        print("    Hinweis: Erste KI-Analyse kann 2–3 Minuten dauern (phi3 ist langsam auf CPU).")

    print("\nDatenbank prüfen:")
    db_ok, db_message = check_database()
    if db_ok:
        print(f"  OK: {db_message}")
    else:
        print(f"  ⚠️ Datenbankprüfung fehlgeschlagen: {db_message}")
        print("    Bitte starten Sie den MySQL-Server und prüfen Sie die Zugangsdaten in agent.py / db_setup.py.")

    print("\nHinweis:")
    print("  - Installieren Sie die Python-Abhängigkeiten mit: python -m pip install -r requirements.txt")
    print("  - Starten Sie ggf. die Datenbank und prüfen Sie die Konfiguration in agent.py/db_setup.py.")
    print("  - Die App läuft auch ohne DB/Ollama dank flight_data.py (regelbasierter Fallback).")

    packages_ok = all(available for _, available, _ in package_results)
    app_ready = python_ok and packages_ok

    if app_ready and api_ok and db_ok:
        print("\n✅ Alle Checks bestanden (Python, Pakete, Ollama, Datenbank).")
        return 0
    if app_ready:
        print("\n✅ App startbereit (Python + Pakete). Ollama/DB optional – siehe Hinweise oben.")
        return 0
    print("\n❌ Pflicht-Checks fehlgeschlagen. Bitte beheben Sie die oben genannten Probleme.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
