from flask import Flask, jsonify, render_template, request
import requests
import random

app = Flask(__name__)

# Load tree data once at startup from NYC Open Data API (limit to 1000 for performance)
def load_trees():
    print("Loading tree data...")
    url = "https://data.cityofnewyork.us/resource/nwxe-4ae8.json?$limit=1000"
    try:
        response = requests.get(url)
        response.raise_for_status()
        trees = response.json()
        print(f"Loaded {len(trees)} trees.")
        return trees
    except Exception as e:
        print(f"Error loading tree data: {e}")
        return []

# Global variable holding tree dataset
trees_data = load_trees()

def get_random_tree():
    """Return a random tree with coordinates and image URL (using static map of tree location)."""
    # Filter trees with valid lat/lon
    valid_trees = [t for t in trees_data if 'latitude' in t and 'longitude' in t]

    if not valid_trees:
        return None

    tree = random.choice(valid_trees)

    lat = tree.get('latitude')
    lon = tree.get('longitude')
    species = tree.get('spc_common', 'Unknown species')
    borough = tree.get('boroname', 'Unknown borough')

    # Generate a static map image URL using OpenStreetMap (via MapQuest Static Map)
    # (You can replace with any free static map provider or custom image)
    # For demo: use OpenStreetMap Static Map tile server (basic example)
    zoom = 18
    size = "400x300"
    # We'll create a simple static OSM tile URL with a marker (using OpenStreetMap)
    # Because OSM doesn't have a native static API, use a third party or generate custom
    # For simplicity, just link to a normal tile URL (won't have marker) — replace if you want
    static_map_url = f"https://static-maps.yandex.ru/1.x/?ll={lon},{lat}&size=400,300&z={zoom}&l=map&pt={lon},{lat},pm2rdm"

    return {
        "latitude": lat,
        "longitude": lon,
        "species": species,
        "borough": borough,
        "image_url": static_map_url
    }

@app.route("/")
def index():
    """Serve the home page with a Start button."""
    return render_template("index.html")

@app.route("/game")
def game():
    """Serve the game page with a random tree location."""
    tree = get_random_tree()
    if tree is None:
        return "No tree data available.", 500
    return render_template("game.html", tree=tree)

@app.route("/api/tree")
def api_tree():
    """API endpoint to get a new random tree."""
    tree = get_random_tree()
    if tree is None:
        return jsonify({"error": "No tree data available"}), 500
    return jsonify(tree)

if __name__ == "__main__":
    # Run Flask app
    app.run(debug=True)