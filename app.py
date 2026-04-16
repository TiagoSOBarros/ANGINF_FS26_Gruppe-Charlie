from flask import Flask, render_template, jsonify
import sqlite3
import requests
from datetime import datetime

app = Flask(__name__)
DB_NAME = "weather.db"

CANTONS = {
    "ZH": {"name": "Zürich", "lat": 47.3769, "lon": 8.5417},
    "BE": {"name": "Bern", "lat": 46.9480, "lon": 7.4474},
    "LU": {"name": "Luzern", "lat": 47.0502, "lon": 8.3093},
    "AG": {"name": "Aargau", "lat": 47.3925, "lon": 8.0442},
    "AI": {"name": "Appenzell Innerrhoden", "lat": 47.3310, "lon": 9.4096},
    "AR": {"name": "Appenzell Ausserrhoden", "lat": 47.3861, "lon": 9.2792},
    "BL": {"name": "Basel-Landschaft", "lat": 47.4848, "lon": 7.7367},
    "BS": {"name": "Basel-Stadt", "lat": 47.5596, "lon": 7.5886},
    "FR": {"name": "Fribourg", "lat": 46.8065, "lon": 7.1618},
    "GE": {"name": "Genève", "lat": 46.2044, "lon": 6.1432},
    "GL": {"name": "Glarus", "lat": 47.0404, "lon": 9.0679},
    "GR": {"name": "Graubünden", "lat": 46.8543, "lon": 9.5259},
    "JU": {"name": "Jura", "lat": 47.3649, "lon": 7.3451},
    "NE": {"name": "Neuchâtel", "lat": 46.9920, "lon": 6.9319},
    "NW": {"name": "Nidwalden", "lat": 46.9580, "lon": 8.3661},
    "OW": {"name": "Obwalden", "lat": 46.8961, "lon": 8.2458},
    "SG": {"name": "St. Gallen", "lat": 47.4245, "lon": 9.3767},
    "SH": {"name": "Schaffhausen", "lat": 47.6973, "lon": 8.6349},
    "SO": {"name": "Solothurn", "lat": 47.2088, "lon": 7.5324},
    "SZ": {"name": "Schwyz", "lat": 47.0207, "lon": 8.6541},
    "TG": {"name": "Thurgau", "lat": 47.5581, "lon": 8.8988},
    "TI": {"name": "Ticino", "lat": 46.1946, "lon": 9.0236},
    "UR": {"name": "Uri", "lat": 46.8804, "lon": 8.6444},
    "VD": {"name": "Vaud", "lat": 46.5197, "lon": 6.6323},
    "VS": {"name": "Valais", "lat": 46.2331, "lon": 7.3606},
    "ZG": {"name": "Zug", "lat": 47.1662, "lon": 8.5155}
}

# ---------------- Wettercode-Mapping ----------------

def map_weather_text(code):
    if code == 0:
        return "Sonnig"
    if code in [1, 2, 3]:
        return "Teilweise bewölkt"
    if code in [45, 48]:
        return "Nebel"
    if code in [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82]:
        return "Regen"
    if code in [71, 73, 75, 77, 85, 86]:
        return "Schnee"
    if code in [95, 96, 99]:
        return "Gewitter"
    return "Unbekannt"

def map_weather_icon(code):
    if code == 0:
        return "fa-sun"
    if code in [1, 2, 3]:
        return "fa-cloud-sun"
    if code in [45, 48]:
        return "fa-smog"
    if code in [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82]:
        return "fa-cloud-rain"
    if code in [71, 73, 75, 77, 85, 86]:
        return "fa-snowflake"
    if code in [95, 96, 99]:
        return "fa-bolt"
    return "fa-cloud"

# ---------------- DB ----------------

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS weather (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        canton TEXT,
        name TEXT,
        temperature REAL,
        humidity REAL,
        apparent REAL,
        wind REAL,
        weather_code INTEGER,
        timestamp TEXT
    )
    """)
    conn.commit()
    conn.close()

# ---------------- API ----------------

def fetch_weather(canton):
    data = CANTONS[canton]

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={data['lat']}&longitude={data['lon']}"
        f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
        f"wind_speed_10m,weather_code&timezone=Europe%2FZurich"
    )

    r = requests.get(url, timeout=10)
    r.raise_for_status()

    current = r.json().get("current")
    if not current:
        raise RuntimeError("Keine aktuellen Wetterdaten erhalten")

    return {
        "canton": canton,
        "name": data["name"],
        "temperature": current.get("temperature_2m"),
        "humidity": current.get("relative_humidity_2m"),
        "apparent": current.get("apparent_temperature"),
        "wind": current.get("wind_speed_10m"),
        "weather_code": current.get("weather_code"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# ---------------- DB speichern ----------------

def save_weather(w):
    conn = get_db()
    conn.execute("""
        INSERT INTO weather
        (canton, name, temperature, humidity, apparent, wind, weather_code, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        w["canton"], w["name"], w["temperature"],
        w["humidity"], w["apparent"], w["wind"],
        w["weather_code"], w["timestamp"]
    ))
    conn.commit()
    conn.close()

# ---------------- DB lesen ----------------

def get_latest(canton):
    conn = get_db()
    row = conn.execute("""
        SELECT * FROM weather
        WHERE canton = ?
        ORDER BY id DESC
        LIMIT 1
    """, (canton,)).fetchone()
    conn.close()
    return row

# ---------------- ROUTES ----------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/weather/<canton>")
def weather(canton):
    canton = canton.upper()

    if canton not in CANTONS:
        return jsonify({"error": "Kanton nicht gefunden"}), 404

    try:
        w = fetch_weather(canton)
        save_weather(w)
        db_data = get_latest(canton)

        if not db_data:
            return jsonify({"error": "Keine gespeicherten Daten"}), 500

        return jsonify({
            "ort": db_data["name"],
            "temperatur": db_data["temperature"],
            "luftfeuchtigkeit": db_data["humidity"],
            "apparent": db_data["apparent"],
            "wind": db_data["wind"],
            "weathercode": db_data["weather_code"],
            "wetterart": map_weather_text(db_data["weather_code"]),
            "icon": map_weather_icon(db_data["weather_code"])
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
