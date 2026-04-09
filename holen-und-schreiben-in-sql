import os
import sqlite3
import requests
from datetime import datetime

DB_DATEI = "wetterdaten.db"


def initialisiere_datenbank(db_datei=DB_DATEI):
    """Erstellt die SQLite-Tabelle, falls sie noch nicht existiert."""
    with sqlite3.connect(db_datei) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wetterdaten (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zeitstempel TEXT NOT NULL,
                ort TEXT NOT NULL,
                temperatur_c REAL NOT NULL,
                luftfeuchtigkeit INTEGER NOT NULL
            )
        """)
        conn.commit()


def speichere_in_sqlite(temperatur_c, luftfeuchtigkeit, ort, db_datei=DB_DATEI):
    """
    Schreibt Temperatur und Luftfeuchtigkeit in die SQLite-Datenbank.
    Diese Funktion erhält die Daten von einer anderen Funktion.
    """
    zeitstempel = datetime.now().isoformat(timespec="seconds")

    with sqlite3.connect(db_datei) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO wetterdaten (
                zeitstempel, ort, temperatur_c, luftfeuchtigkeit
            ) VALUES (?, ?, ?, ?)
        """, (zeitstempel, ort, temperatur_c, luftfeuchtigkeit))
        conn.commit()


def hole_wetterdaten(ort, api_key):
    """
    Holt aktuelle Wetterdaten von OpenWeather
    und gibt Temperatur und Luftfeuchtigkeit zurück.
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": ort,
        "appid": api_key,
        "units": "metric"   # Temperatur in °C
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    daten = response.json()

    temperatur_c = daten["main"]["temp"]
    luftfeuchtigkeit = daten["main"]["humidity"]

    return temperatur_c, luftfeuchtigkeit


def main():
    initialisiere_datenbank()

    ort = "Lucerne,CH"

    # Empfehlung: API-Key als Umgebungsvariable speichern
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise ValueError("Bitte setze die Umgebungsvariable OPENWEATHER_API_KEY.")

    temperatur_c, luftfeuchtigkeit = hole_wetterdaten(ort, api_key)
    speichere_in_sqlite(temperatur_c, luftfeuchtigkeit, ort)

    print(f"Gespeichert: {ort} | {temperatur_c} °C | {luftfeuchtigkeit} %")


if __name__ == "__main__":
    main()
