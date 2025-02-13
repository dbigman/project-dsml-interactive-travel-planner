from flask import Flask, jsonify, send_from_directory
import json
import os
import logging
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

# Load environment variables from .env file
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_MAPS_API_KEY:
    logging.error("Google API key is missing! Check your .env file.")
    raise ValueError("Google API key not found.")

# Load landmarks from JSON file
def load_json_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"{filename} not found!")
        return []
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from {filename}")
        return []

landmarks = load_json_file("landmarks_corrected.json")
municipalities = load_json_file("municipalities_corrected.json")  

@app.route('/get_locations', methods=['GET'])
def get_locations():
    return jsonify({"landmarks": landmarks, "municipalities": municipalities})

@app.route("/")
def serve_index():
    return send_from_directory("static", "index.html")

if __name__ == '__main__':
    app.run(debug=True)
