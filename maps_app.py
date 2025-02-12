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
    """Load landmarks from a JSON file.

    This function attempts to open a specified JSON file and load its
    contents. If the file is found and contains valid JSON, it returns the
    parsed data. If the file is not found or if there is an error decoding
    the JSON, it logs an error message and returns an empty list.

    Args:
        filename (str): The path to the JSON file to be loaded.

    Returns:
        list: The contents of the JSON file as a list, or an empty list if
        an error occurs.
    """

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
