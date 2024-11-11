#######
#Formål med dette scriptet var å teste ut og bygge en fungerende terimnal GPT før den ble implementert med gradio
#Du interagerer dermed med GPTen i terimnal og avslutter med "quit()"
#Enedelig implementasjon er i Date_GPT_deployed.py
######

import openai
import os
import json
from scipy.spatial.distance import cosine
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

#Find the correct root directory (Assingment 2)
script_dir = Path(__file__).resolve().parent
os.chdir(script_dir)


# Hent API key til open ai bibloteket og gi den til openai objektet
###
# Note: For å redprodusere koden må du genere din egen API kode fra Open AI sine utviklertjenster
###
with open("Data/API_KEY.txt", 'r') as file:
    api_key = file.read().strip()
openai.api_key = api_key

# Load Json bergen objektet
with open('Data/bergen_embedded_data.json', 'r') as file:
    bergen_embedding_data = json.load(file)

def embed_text(text):
    reply = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=text,
        encoding_format="float"
    )
    return reply.data[0].embedding

def find_best_match(user_input, embeddings):
    user_embedding = embed_text(user_input)  # Generate an embedding for the user input
    similarities = []
    highest_similarity = -1

    for category, subcategories in embeddings.items():
        for subcategory, entries in subcategories.items():
            for entry in entries:
                similarity = cosine_similarity([user_embedding], [entry['embedding']])
                similarities.append((similarity, entry))
                if similarity > highest_similarity:
                    highest_similarity = similarity
                    best_match = entry

    # Sort by similarity score and pick top 5 and return just the description (not embedding values)
    similarities.sort(reverse=True, key=lambda x: x[0])
    similarities = similarities[:5]
    return [similarity[1] for similarity in similarities] if similarities else None

def ny_promt_med_forslag(user_input, beste_matcher):
    if isinstance(beste_matcher, dict):
        beste_matcher = [beste_matcher]

    forslag = "\n".join([f"- {match['beskrivelse']}" for match in beste_matcher])
    ny_prompt = (f"Brukeren har gitt følgende input: '{user_input}' : \n\n"
                 f"Under følger forslag fra søk i databasen: \n"
                 f"{forslag}"
                 f"Venligste besvar forespørselen, forslagene er kun ment til hjelp"
                 )

    return ny_prompt

GPT_model = "gpt-3.5-turbo"
messages = []

system_msg = """ 
    Du er en KI chatbot som planlegger dates i Bergen/Hordalands området. 
    Du svarer kun på norsk (forklarer eventuelt at dette er en begrensning du har ved behov).
    Du prøver så godt som mulig å tilpasse svaret ditt etter spesifiseringen gitt av brukeren.
        
    For at dateplanen skal være så ferdig som mulig larger du en plan med ulike aktiviteter som bør foregå
    sekvensielt, fra den ene forslåtte aktiviteten til den neste. 
    Hvis du får budsjett eller andre behov spesifisert tar du hensyn til dette. 

    Hvis ikke angitt etterspør sessong så du vet værforholdene på året så du kan tilpasse forslagene dine etter sesong. 
    """
messages.append({"role": "system", "content": [{"type" : "text", "text" : system_msg}]})

print("Fortell dine ønsker for å utforme den beste daten mulig!")


while True:
    message = input()

    #Sjekk om avslutte programmet
    if(message.lower() == "quit()"):
        print("Exiting chat...")
        break
    
    #Embedding
    best_matches = find_best_match(message, bergen_embedding_data)
    #print(best_matches)

    if best_matches: 
        message = ny_promt_med_forslag(message, best_matches)
        messages.append({"role": "user", "content": [{"type" : "text", "text" : message}] })
    else: 
        messages.append({"role": "user", "content": [{"type" : "text", "text" : message}] })

    response = openai.chat.completions.create(
        model = GPT_model,
        messages = messages)
    
    reply = response.choices[0].message.content
    
    messages.append({"role": "assistant", "content": [{"type" : "text", "text" : reply }] })
    print("\n" + reply + "\n")
    
