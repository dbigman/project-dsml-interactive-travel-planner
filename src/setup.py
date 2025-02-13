# %% [markdown]
# <a href="https://colab.research.google.com/github/dbigman/project-dsml-interactive-travel-planner/blob/main/Final_project_IH.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# %% [markdown]
# # The Hithchiker's Guide to Puerto Rico
# In this project, we are going to use all the Data Science and Machine Learning skills we have acquired during the course of the last few weeks to build an interactive travel planner for the beautiful island of Puerto Rico. By the end of this project, we will present a working application that cooperates with a visitor to help them build a travel itinerary suitable to their personal preferences.

# %%
# Imports
import os
import requests

import json
from bs4 import BeautifulSoup
import re
import html


# %% [markdown]
# ## From HTML to .JSON|

# %% [markdown]
# ### Functions

# %%
# Function to clean unwanted characters and fix words
def clean_text(text):
    # Remove unwanted characters (e.g., escape sequences like "\xc9")
    text = re.sub(r'\\[xX][0-9A-Fa-f]{2}', '', text)  # Remove escaped Unicode characters
    text = re.sub(r'[\r\n\t]', ' ', text)  # Remove newlines and tabs
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with one
    text = text.strip()  # Remove leading and trailing spaces
    return text

# Function to add missing characters like 'ñ'
def add_missing_characters(text):
    # Mapping of words that might need 'ñ' or other fixes
    replacements = {
        "Aguada": "Aguada",
        "Aasco": "Añasco",
        "Catao": "Cataño",
        "Nio": "Niño",
        "Peuelas": "Peñuelas"
        # Add other common words as needed
    }

    # Replace words based on the mapping
    for wrong_word, correct_word in replacements.items():
        text = re.sub(rf'\b{wrong_word}\b', correct_word, text, flags=re.IGNORECASE)
    return text

# Function to extract coordinates from the HTML content
def extract_coordinates(html_content):
    # Regex pattern to match lat and lon inside "wgCoordinates"
    coordinates_pattern = r'"wgCoordinates":\s*\{\s*"lat":\s*(-?\d+\.\d+),\s*"lon":\s*(-?\d+\.\d+)\s*\}'
    match = re.search(coordinates_pattern, html_content)

    if match:
        # Clean and extract latitude and longitude as float values
        lat = float(match.group(1).strip().replace("\\n", ""))  # Remove any unwanted newline characters
        lon = float(match.group(2).strip().replace("\\n", ""))  # Remove any unwanted newline characters
        return lat, lon

    return None, None

# %% [markdown]
# ### Municipalities

# %%
# Path to the municipalities folder in Google Drive
municipalities_folder = "/content/drive/MyDrive/IronHack_final_project/municipalities"

# List to store structured data
municipalities_data = []

# Loop through each .txt file in the folder
for filename in os.listdir(municipalities_folder):
    if filename.endswith(".txt"):  # Ensure we only process .txt files
        file_path = os.path.join(municipalities_folder, filename)

        # Read the HTML content
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        # Parse HTML using BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract title (or use filename if no title found), and clean it
        title = clean_text(soup.title.string) if soup.title else clean_text(filename.replace(".txt", ""))
        # Remove " - Wikipedia" from the title
        title = title.replace(" - Wikipedia", "")
        title = add_missing_characters(title)  # Add missing characters to the title

        # Extract first 3 paragraphs for description
        paragraphs = [clean_text(p.get_text(strip=True)) for p in soup.find_all("p")][:3]
        paragraphs = [add_missing_characters(p) for p in paragraphs]  # Add missing characters to description

        # Extract coordinates (latitude and longitude) from HTML content
        latitude, longitude = extract_coordinates(html_content)

        # Structure the data
        municipality = {
            "name": title,
            "category": "Municipality",
            "description": paragraphs,
            "coordinates": {
                "latitude": latitude,
                "longitude": longitude
            },
            "source_file": filename
        }

        # Append to the list
        municipalities_data.append(municipality)

# Save structured data as JSON
output_json = "/content/drive/MyDrive/IronHack_final_project/municipalities.json"
with open(output_json, "w", encoding="utf-8") as json_file:
    json.dump(municipalities_data, json_file, indent=4, ensure_ascii=False)

print(f"Municipality data with coordinates saved as {output_json}")

# %% [markdown]
# ### Landmarks

# %%
# Path to the landmarks folder in Google Drive
landmarks_folder = "/content/drive/MyDrive/IronHack_final_project/landmarks"

# List to store structured data
landmarks_data = []

# Loop through each .txt file in the folder
for filename in os.listdir(landmarks_folder):
    if filename.endswith(".txt"):  # Ensure we only process .txt files
        file_path = os.path.join(landmarks_folder, filename)

        # Read the HTML content
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        # Parse HTML using BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract title (or use filename if no title found)
        title = soup.title.string if soup.title else filename.replace(".txt", "")
        title = clean_text(title)  # Clean the title text

        # Extract first 3 paragraphs for description
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")][:3]
        paragraphs = [clean_text(paragraph) for paragraph in paragraphs]  # Clean description paragraphs

        # Extract coordinates (if available)
        lat, lon = extract_coordinates(html_content)
        coordinates = {"latitude": lat, "longitude": lon} if lat and lon else None

        # Find the municipality (look for it in the text)
        municipality = None
        if "municipality" in html_content.lower():
            municipality_match = re.search(r"Municipality of\s+([A-Za-z\s]+)", html_content)
            if municipality_match:
                municipality = clean_text(municipality_match.group(1))  # Clean municipality text

        # Structure the data
        landmark = {
            "name": title,
            "category": "Landmark",
            "description": paragraphs,
            "coordinates": coordinates,
            "municipality": municipality,
            "source_file": filename
        }

        # Append to the list
        landmarks_data.append(landmark)

# Save structured data as JSON
output_json = "/content/drive/MyDrive/IronHack_final_project/landmarks.json"
with open(output_json, "w", encoding="utf-8") as json_file:
    json.dump(landmarks_data, json_file, indent=4, ensure_ascii=False)

print(f"Landmark data saved as {output_json}")

# %% [markdown]
# ## News

# %%
# Navigate to the correct folder
data_dir = "/content/drive/MyDrive/IronHack_final_project/elmundo_chunked_es_page1_40years"
files = os.listdir(data_dir)

print(f"Total files: {len(files)}")
print("Sample files:", files[:5])  # Preview first 5 files
file_sizes = {file: os.path.getsize(os.path.join(data_dir, file)) for file in files}
print(f"Average file size: {sum(file_sizes.values()) / len(file_sizes):.2f} bytes")
print("Smallest files:", sorted(file_sizes.items(), key=lambda x: x[1])[:5])
print("Largest files:", sorted(file_sizes.items(), key=lambda x: x[1], reverse=True)[:5])

# %% [markdown]
# ## Exploratory Data Analysis

# %%



