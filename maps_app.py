from flask import Flask, jsonify, send_from_directory
import requests
from dotenv import load_dotenv
import logging
import os

app = Flask(__name__)

load_dotenv()

# Load environment variables from .env file
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_MAPS_API_KEY:
    logging.error("Google API key is missing! Check your .env file.")
    raise ValueError("Google API key not found.")

# gps coordinates landmarks
landmarks = [
    {"name": "El Yunque", "lat": 18.2956, "lng": -65.8024},
    {"name": "Old San Juan", "lat": 18.4655, "lng": -66.1165},
    {"name": "Culebra", "lat": 18.3167, "lng": -65.3000}
]
# gps coordinates muni

municipalities = [
    {"name": "Adjuntas", "lat": 18.163485, "lng": -66.723158},
    {"name": "Aguada", "lat": 18.380158, "lng": -67.188704},
    {"name": "Aguadilla", "lat": 18.427445, "lng": -67.154070},
    {"name": "Aguas Buenas", "lat": 18.256899, "lng": -66.102944},
    {"name": "Aibonito", "lat": 18.140702, "lng": -66.259681},
    {"name": "Añasco", "lat": 18.285448, "lng": -67.140293},
    {"name": "Arecibo", "lat": 18.444247, "lng": -66.646407},
    {"name": "Arroyo", "lat": 17.992508, "lng": -66.054582},
    {"name": "Barceloneta", "lat": 18.454706, "lng": -66.538389},
    {"name": "Bayamón", "lat": 18.389396, "lng": -66.165322},
    {"name": "Cabo Rojo", "lat": 18.087535, "lng": -67.146996},
    {"name": "Caguas", "lat": 18.238799, "lng": -66.035249},
    {"name": "Camuy", "lat": 18.451728, "lng": -66.853575},
    {"name": "Canóvanas", "lat": 18.374875, "lng": -65.899753},
    {"name": "Carolina", "lat": 18.380326, "lng": -65.962621},
    {"name": "Cataño", "lat": 18.446535, "lng": -66.135578},
    {"name": "Cayey", "lat": 18.111905, "lng": -66.166000},
    {"name": "Ceiba", "lat": 18.261914, "lng": -65.648106},
    {"name": "Cidra", "lat": 18.175791, "lng": -66.161278},
    {"name": "Coamo", "lat": 18.079962, "lng": -66.357947},
    {"name": "Comerío", "lat": 18.221098, "lng": -66.223440},
    {"name": "Corozal", "lat": 18.341012, "lng": -66.317427},
    {"name": "Dorado", "lat": 18.458835, "lng": -66.267668},
    {"name": "Fajardo", "lat": 18.325787, "lng": -65.652384},
    {"name": "Guánica", "lat": 17.972514, "lng": -66.908626},
    {"name": "Guayama", "lat": 17.984133, "lng": -66.113777},
    {"name": "Guaynabo", "lat": 18.361555, "lng": -66.111068},
    {"name": "Humacao", "lat": 18.155134, "lng": -65.820394},
    {"name": "Isabela", "lat": 18.470386, "lng": -67.024206},
    {"name": "Jayuya", "lat": 18.218567, "lng": -66.591562},
    {"name": "Juana Díaz", "lat": 18.053437, "lng": -66.507508},
    {"name": "Juncos", "lat": 18.227456, "lng": -65.920997},
    {"name": "Lares", "lat": 18.294675, "lng": -66.877121},
    {"name": "Levittown", "lat": 18.449947, "lng": -66.181560},
    {"name": "Loíza", "lat": 18.426430, "lng": -65.880043},
    {"name": "Luquillo", "lat": 18.378986, "lng": -65.720656},
    {"name": "Manatí", "lat": 18.433005, "lng": -66.475858},
    {"name": "Mayagüez", "lat": 18.201345, "lng": -67.145155},
    {"name": "Moca", "lat": 18.394669, "lng": -67.113236},
    {"name": "Naguabo", "lat": 18.211625, "lng": -65.734884},
    {"name": "Patillas", "lat": 18.006354, "lng": -66.015719},
    {"name": "Peñuelas", "lat": 18.063358, "lng": -66.727390},
    {"name": "Ponce", "lat": 18.011077, "lng": -66.614062},
    {"name": "Río Grande", "lat": 18.378620, "lng": -65.839334},
    {"name": "Sabana Grande", "lat": 18.077739, "lng": -66.960455},
    {"name": "San Germán", "lat": 18.080708, "lng": -67.041110},
    {"name": "San Juan", "lat": 18.465539, "lng": -66.105735},
    {"name": "San Lorenzo", "lat": 18.189402, "lng": -65.960997},
    {"name": "San Sebastián", "lat": 18.335476, "lng": -66.994679},
    {"name": "Santa Isabel", "lat": 18.004677, "lng": -66.389794},
    {"name": "Toa Alta", "lat": 18.388282, "lng": -66.248224},
    {"name": "Trujillo Alto", "lat": 18.356317, "lng": -66.003384},
    {"name": "Utuado", "lat": 18.265510, "lng": -66.700452},
    {"name": "Vega Alta", "lat": 18.431552, "lng": -66.336510},
    {"name": "Vega Baja", "lat": 18.444391, "lng": -66.387670},
    {"name": "Vieques", "lat": 18.126285, "lng": -65.440098},
    {"name": "Yabucoa", "lat": 18.050520, "lng": -65.879329},
    {"name": "Yauco", "lat": 18.034964, "lng": -66.849898}
]

@app.route('/get_locations', methods=['GET'])
def get_locations():
    return jsonify({"landmarks": landmarks, "municipalities": municipalities})

@app.route("/")
def serve_index():
    return send_from_directory("static", "index.html")

if __name__ == '__main__':
    app.run(debug=True)
