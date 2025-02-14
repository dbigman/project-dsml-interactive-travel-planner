from flask import Flask, jsonify, render_template, send_from_directory
import json
import os
import logging
from dotenv import load_dotenv
import sys
from icecream import ic

# -------------------------
# 1. Logging Setup
# -------------------------
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Remove existing handlers to prevent duplicate logs
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

file_handler = logging.FileHandler("chatbot_correction.log", encoding="utf-8")
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.info("Logging initialized.")


# app = Flask(__name__)
app = Flask(__name__, static_folder='../static')


load_dotenv()

# Load environment variables from .env file
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_MAPS_API_KEY:
    logging.error("Google API key is missing! Check your .env file.")
    raise ValueError("Google API key not found.")

# Load landmarks from JSON files
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

# landmarks = load_json_file("../data/landmarks_corrected.json")
# municipalities = load_json_file("../data/municipalities_corrected.json")  

landmarks = load_json_file("data/landmarks_corrected.json")
municipalities = load_json_file("data/municipalities_corrected.json")
ic(municipalities)

@app.route('/get_locations', methods=['GET'])
def get_locations():
    return jsonify({"landmarks": landmarks, "municipalities": municipalities})

# @app.route("/")
# def serve_index():
#     return send_from_directory("static", "index.html")

# @app.route("/")
# def serve_index():
#     return send_from_directory(app.static_folder, "index.html")


@app.route("/")
def serve_index():
    # Render the template and pass the API key as a variable
    return render_template("index.html", google_maps_api_key=GOOGLE_MAPS_API_KEY)

if __name__ == '__main__':
    app.run(debug=True)
