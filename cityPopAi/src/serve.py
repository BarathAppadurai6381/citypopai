from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="web")
CORS(app)

# Serve index.html from /web
@app.route("/")
def index():
    return send_from_directory("web", "index.html")

# Prediction API
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    city = data.get("city", "").title()
    year = int(data.get("year", 2025))

    # Dummy model: base + growth
    base_population = {
        "Tirupur": 900000,
        "Chennai": 7200000,
        "Coimbatore": 2200000,
        "Madurai": 1600000
    }

    growth_rate = 0.012  # 1.2% per year

    if city in base_population:
        population = int(base_population[city] * ((1 + growth_rate) ** (year - 2025)))
    else:
        population = int(100000 * ((1 + growth_rate) ** (year - 2025)))

    return jsonify({
        "city": city,
        "year": year,
        "predicted_population": population
    })

if __name__ == "__main__":
    app.run(debug=True)
