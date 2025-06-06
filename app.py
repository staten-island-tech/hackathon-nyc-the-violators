from flask import Flask, render_template, request, jsonify
import random
import math

app = Flask(__name__)

# --- NYC Borough coordinate ranges (approximate bounding boxes) ---
BOROUGH_COORDINATES = {
    "Manhattan": {"lat": (40.700, 40.880), "lon": (-74.020, -73.930)},
    "Brooklyn": {"lat": (40.570, 40.740), "lon": (-74.040, -73.850)},
    "Queens": {"lat": (40.540, 40.800), "lon": (-73.960, -73.700)},
    "Bronx": {"lat": (40.790, 40.910), "lon": (-73.930, -73.780)},
    "Staten Island": {"lat": (40.480, 40.650), "lon": (-74.260, -74.050)},
}

# Generate a random location within one of the five boroughs
def generate_location():
    borough = random.choice(list(BOROUGH_COORDINATES.keys()))
    coords = BOROUGH_COORDINATES[borough]
    lat = round(random.uniform(*coords["lat"]), 6)
    lon = round(random.uniform(*coords["lon"]), 6)
    return {"borough": borough, "latitude": lat, "longitude": lon}

# Calculate distance using the Haversine formula (in kilometers)
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return round(R * c, 2)

# --- Flask Routes ---

# Homepage: title, description, start button
@app.route("/")
def home():
    return render_template("home.html")

# Start game: render map with random location as the hidden answer
@app.route("/start")
def start_game():
    location = generate_location()
    return render_template("game.html", actual_lat=location["latitude"], actual_lon=location["longitude"])

# Submit user guess: compare with actual location and return score
@app.route("/submit_guess", methods=["POST"])
def submit_guess():
    data = request.json
    guess_lat = data.get("lat")
    guess_lon = data.get("lon")
    actual_lat = data.get("actual_lat")
    actual_lon = data.get("actual_lon")

    # Error handling
    if None in [guess_lat, guess_lon, actual_lat, actual_lon]:
        return jsonify({"error": "Missing coordinates"}), 400

    # Calculate score based on distance
    distance = calculate_distance(guess_lat, guess_lon, actual_lat, actual_lon)
    score = max(0, round(1000 - distance * 10))  # Simple scoring model

    return jsonify({"distance_km": distance, "score": score})

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)