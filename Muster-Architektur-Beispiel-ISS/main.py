import time
import requests

from database import init_db, insert_location

API_URL = "http://api.open-notify.org/iss-now.json"
INTERVAL_SECONDS = 5


def fetch_iss_location() -> tuple[float, float, int]:
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()

    payload = response.json()

    if payload.get("message") != "success":
        raise RuntimeError(f"API meldet keinen Erfolg: {payload}")

    position = payload["iss_position"]
    latitude = float(position["latitude"])
    longitude = float(position["longitude"])
    fetched_at = int(payload["timestamp"])

    return latitude, longitude, fetched_at


def run_once() -> None:
    latitude, longitude, fetched_at = fetch_iss_location()
    insert_location(latitude, longitude, fetched_at)
    print(
        f"Gespeichert: latitude={latitude}, longitude={longitude}, timestamp={fetched_at}"
    )


def main() -> None:
    init_db()

    while True:
        try:
            run_once()
        except requests.RequestException as exc:
            print(f"Netzwerkfehler: {exc}")
        except Exception as exc:
            print(f"Fehler: {exc}")

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()