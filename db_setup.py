import mysql.connector

from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER


def check_database():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        )
        cursor = conn.cursor()

        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Erfolgreich verbunden mit Datenbank: {DB_NAME}")
        print(f"Vorhandene Tabellen: {', '.join(tables)}")

        required = ["flight", "booking", "airport", "airplane"]
        missing = [t for t in required if t not in tables]

        if missing:
            print(f"Warnung: Folgende benötigte Tabellen fehlen: {', '.join(missing)}")
        else:
            cursor.execute("SELECT COUNT(*) FROM airport")
            airports = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM airplane")
            airplanes = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM flight")
            flights = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM booking")
            bookings = cursor.fetchone()[0]

            print("Datenbankstruktur ist vollständig und bereit.")
            print(f"Statistiken: {airports} Flughäfen, {airplanes} Flugzeuge, {flights} Flüge, {bookings} Buchungen")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Fehler bei der Verbindung zur Datenbank: {e}")


if __name__ == "__main__":
    check_database()
