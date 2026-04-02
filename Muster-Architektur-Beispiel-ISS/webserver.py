from flask import Flask, jsonify, render_template
from database import init_db, get_all_locations

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("positions_chart.html") 


@app.route("/locations")
def locations():
    rows = get_all_locations()
    return jsonify([
        {
            "id": row["id"],
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "fetched_at": row["fetched_at"]
        }
        for row in rows
    ])


def main():
    init_db()
    app.run(debug=True)


if __name__ == "__main__":
    main()