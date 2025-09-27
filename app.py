from flask import Flask, render_template, request, jsonify
import networkx as nx

app = Flask(__name__)

# CORS fix without flask_cors - IMPORTANT!
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

# Flight graph (weights = distance in km)
flight_graph = nx.DiGraph()
flight_graph.add_weighted_edges_from([
    # Tamil Nadu / Domestic
    ("MAA", "IXM", 425), ("MAA", "SXV", 315), 
    ("IXM", "SXV", 160), ("MAA", "BLR", 290),
    ("BLR", "HYD", 475), ("HYD", "DEL", 1320),
    ("BLR", "BOM", 840), ("BOM", "DEL", 1400),
    
    # International
    ("DEL", "JFK", 6780), ("BOM", "LHR", 8300),
    ("BOM", "DXB", 2100), ("SIN", "SYD", 6300),
    ("SFO", "LAX", 540), ("JFK", "ORD", 1200),
    ("ORD", "DFW", 1290), ("DFW", "LAX", 1990),
    ("LHR", "CDG", 344), ("CDG", "DXB", 5250),
    ("DXB", "SIN", 5800),
    
    # Additional routes
    ("MAA", "HYD", 515), ("IXM", "BLR", 400),
    ("SXV", "BLR", 175), ("DEL", "HYD", 1260),
    ("BOM", "HYD", 620), ("MAA", "SIN", 2700),
    ("BLR", "DXB", 2550), ("DEL", "DXB", 2200),
    ("DEL", "LHR", 6700), ("JFK", "LAX", 3950),
    ("LAX", "SFO", 550), ("LHR", "JFK", 5540),
    ("DXB", "LHR", 5500), ("SIN", "SYD", 6300)
])

# Make bidirectional
for u, v, w in list(flight_graph.edges(data='weight')):
    if not flight_graph.has_edge(v, u):
        flight_graph.add_edge(v, u, weight=w)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/find_route", methods=["POST"])
def find_route():
    data = request.json or {}
    source = data.get("source")
    destination = data.get("destination")

    if not source or not destination:
        return jsonify({"error": "Source and destination required."}), 400

    if source not in flight_graph or destination not in flight_graph:
        return jsonify({"error": "Invalid airport code!"}), 400

    if source == destination:
        return jsonify({"error": "Source and destination cannot be the same."}), 400

    try:
        path = nx.shortest_path(flight_graph, source, destination, weight="weight")
        total_distance = nx.shortest_path_length(flight_graph, source, destination, weight="weight")
        return jsonify({"path": path, "distance": total_distance})
    except nx.NetworkXNoPath:
        return jsonify({"error": "No available route!"}), 404

if __name__ == "__main__":
    app.run(debug=True)