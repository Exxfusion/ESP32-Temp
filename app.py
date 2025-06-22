from flask import Flask, request, render_template_string
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
