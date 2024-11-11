######################
#Test script for å lage en embeeded datatabell i Python med informasjon i txt dokumentene (Bergen_...)   
#Må kjøres før Date_GPT_deplyoed.py for at denne skal ha den embeddede json filen tilgjenglig
####################

import openai
from scipy.spatial.distance import cosine
import os
import json
from pathlib import Path

#Find the correct root directory (Assingment 2)
script_dir = Path(__file__).resolve().parent
os.chdir(script_dir)

# Try to get the API key from the environment variable (for hugging face space)
api_key = os.getenv('API_key')

# If the environment variable is not set, read from the file
if not api_key:
    try:
        with open("Data/API_KEY.txt", 'r') as file:
            api_key = file.read().strip()
        print("API key loaded from file.")
    except FileNotFoundError:
        raise FileNotFoundError("API key not found in the environment variable or file.")

# Check if the API key was successfully loaded
if not api_key:
    raise ValueError("API key is missing! Please set the API_KEY environment variable or place it in 'Data/API_KEY.txt'.")

# Define a function to parse files with headers
def parse_file(file_paths):
    data = {}
    current_category = None
    with open(file_paths, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:  # Skip empty lines
                continue
            if line.isupper():  # Assuming headers are in uppercase
                current_category = line
                data[current_category] = []  # New category
            elif current_category:
                data[current_category].append(line)
    return data

#Embeddings of txt files
def embed_text(text):
    reply = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=text,
        encoding_format="float"
    )
    return reply.data[0].embedding

# Load each file separately
bergen_sesong = parse_file("Data/Bergen_sessong_forslag.txt")
bergen_spisesteder = parse_file("Data/Bergen_resturanter.txt")
bergen_aktiviteter = parse_file("Data/Bergen_aktiviteter.txt")

#Create common directory object for all the files
bergen_txt = {"Spisesteder" : bergen_spisesteder, "Sesong_aktiviteter" : bergen_sesong, "Generelle_aktiviteter" : bergen_aktiviteter}

embeeded_data = {}
for kategori, subkategori in bergen_txt.items():
    embeeded_data[kategori] = {}
    for subkategori, beskrivelse in subkategori.items():
        embeeded_data[kategori][subkategori] = []
        for beskrivelse in beskrivelse: 
            embedding = embed_text(beskrivelse)
            embeeded_data[kategori][subkategori].append({
                "beskrivelse" : beskrivelse,
                "embedding" : embedding
            })  

# Assuming 'embedded_data' is your dictionary containing embeddings
with open('Data/bergen_embedded_data.json', 'w') as f:
    json.dump(embeeded_data, f) 