from flask import Flask, request
import os

app = Flask(__name__)
data = {}

@app.route("/api/data", methods=["POST"])
def api_data():
    json_data = request.get_json()
    if json_data:
        data[json_data["sensor"]] = json_data
    return {"status": "ok"}

@app.route("/")
def index():
    html = "<h1>Keller Werte</h1>"
    for sensor, d in data.items():
        html += f"<p>{sensor}: {d['temp']}°C, {d['hum']}% Luftfeuchte</p>"
    return html

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
