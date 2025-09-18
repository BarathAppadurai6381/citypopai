from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import os
import numpy as np
from sklearn.linear_model import LinearRegression

# Initialize Flask
app = Flask(__name__, static_folder="web")
CORS(app)

# ======================
# Load dataset
# ======================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "data", "city_demographics.csv")

df = pd.read_csv(csv_path)

# Normalize column names
df.columns = df.columns.str.strip().str.lower()

required_cols = {"city", "year", "total_population", "male_ratio", "female_ratio", "voter_ratio"}
missing = required_cols - set(df.columns)
if missing:
    raise ValueError(f"Your CSV is missing columns: {', '.join(missing)}")

# Clean data
df["city"] = df["city"].astype(str).str.strip().str.title()
df["year"] = df["year"].astype(int)
df["total_population"] = df["total_population"].astype(int)

# ======================
# Routes
# ======================

@app.route("/")
def index():
    return send_from_directory("web", "index.html")

@app.route("/cities", methods=["GET"])
def get_cities():
    """Return all unique cities for dropdown"""
    cities = sorted(df["city"].unique().tolist())
    return jsonify(cities)

@app.route("/predict", methods=["GET"])
def predict():
    city = request.args.get("city", "").title()
    year = request.args.get("year", type=int)

    if not city or not year:
        return jsonify({"error": "City and year are required"}), 400

    # Filter city data
    city_data = df[df["city"].str.lower() == city.lower()].sort_values("year")

    if city_data.empty:
        return jsonify({"error": f"No data for {city}"}), 404

    # Historical data
    if year in city_data["year"].values:
        row = city_data[city_data["year"] == year].iloc[0]
        return jsonify({
            "city": city,
            "year": year,
            "population": int(row["total_population"]),
            "male_ratio": float(row["male_ratio"]),
            "female_ratio": float(row["female_ratio"]),
            "voter_ratio": float(row["voter_ratio"]),
            "predicted": False
        })

    # Prediction using Linear Regression
    X = city_data[["year"]].values
    y = city_data["total_population"].values
    model = LinearRegression()
    model.fit(X, y)

    predicted_population = int(model.predict(np.array([[year]]))[0])
    last_row = city_data.iloc[-1]

    return jsonify({
        "city": city,
        "year": year,
        "population": predicted_population,
        "male_ratio": float(last_row["male_ratio"]),
        "female_ratio": float(last_row["female_ratio"]),
        "voter_ratio": float(last_row["voter_ratio"]),
        "predicted": True
    })

# ======================
# Run
# ======================
if __name__ == "__main__":
    app.run(debug=True)
