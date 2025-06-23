from flask import Flask, request, jsonify, render_template_string
import csv
import time
import os

app = Flask(__name__)

DATA_FILE = "data.csv"
data_current = {"temp": None, "hum": None, "time": None}

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "temp", "hum"])

@app.route("/api/data", methods=["POST"])
def api_data():
    json_data = request.get_json()
    if json_data:
        t = json_data["temp"]
        h = json_data["hum"]
        ts = int(time.time())
        data_current["temp"] = t
        data_current["hum"] = h
        data_current["time"] = ts

        with open(DATA_FILE, "r") as f:
            rows = list(csv.reader(f))
            if len(rows) > 1 and ts // 60 == int(rows[-1][0]) // 60:
                return {"status": "ok (duplicate minute)"}

        with open(DATA_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([ts, t, h])

    return {"status": "ok"}

@app.route("/chart-data")
def chart_data():
    now = int(time.time())
    min_time = now - 48 * 3600
    labels = []
    temps = []
    hums = []

    with open(DATA_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = int(row["timestamp"])
            if ts >= min_time:
                t_struct = time.localtime(ts + 7200)
                label = time.strftime("%H:%M", t_struct)
                labels.append(label)
                temps.append(float(row["temp"]))
                hums.append(float(row["hum"]))

    return jsonify({"labels": labels, "temps": temps, "hums": hums})

@app.route("/")
def index():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
      <title>Waschküche Werte</title>
      <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
      <style>
        body { background: #e0f7ff; font-family: sans-serif; text-align: center; }
        canvas { background: white; border-radius: 8px; margin: 20px auto; }
      </style>
    </head>
    <body>
      <h1>Waschküche Werte (aktuell)</h1>
      <p>Temp: {{temp}} °C</p>
      <p>Feuchte: {{hum}} %</p>
      <canvas id="tempChart" width="400" height="200"></canvas>
      <canvas id="humChart" width="400" height="200"></canvas>
      <script>
        async function loadData() {
          const res = await fetch('/chart-data');
          const data = await res.json();
          return data;
        }

        loadData().then(data => {
          new Chart(document.getElementById('tempChart').getContext('2d'), {
            type: 'line',
            data: {
              labels: data.labels,
              datasets: [{
                label: 'Temp (°C)',
                data: data.temps,
                borderColor: 'red',
                fill: false
              }]
            }
          });

          new Chart(document.getElementById('humChart').getContext('2d'), {
            type: 'line',
            data: {
              labels: data.labels,
              datasets: [{
                label: 'Feuchte (%)',
                data: data.hums,
                borderColor: 'blue',
                fill: false
              }]
            }
          });
        });
      </script>
    </body>
    </html>
    """
    return render_template_string(html, temp=data_current["temp"], hum=data_current["hum"])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
