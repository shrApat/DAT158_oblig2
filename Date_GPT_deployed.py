#Ferdig implementasjon av LLM date modellen som vil starte en nettside på Gradio

#Fikk desverre ikke css filen til å fugnere med gradio for å endre utsende 
#Har derfor latt css filen bli men slettet forsøket på å implementere det i Gradio

######
#NB: Må kjøre Embedd_data.py først!!!
#Dette vil lage .json filen GPT modellen kan bruke for å søke
#(med mindre filen i GitHub blir brukt, men ved endring av txt filene (Bergen_...) 
# fra nåværende tilstand vil denne .json filen være utdatert)
######


import gradio as gr
import openai
import os
import json
from scipy.spatial.distance import cosine
from sklearn.metrics.pairwise import cosine_similarity
import requests
from datetime import timedelta
from dateutil.parser import parse

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



# Read the API key from the file
#with open("Data/API_KEY.txt", 'r') as file:
#    api_key = file.read().strip()

# Set the API key for OpenAI
openai.api_key = api_key

def fetch_weather_data():
    latitude = "60.39299"  # Bergen's latitude
    longitude = "5.32415"  # Bergen's longitude
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={latitude}&lon={longitude}"
    headers = {"User-Agent": "DatePlannerApp/1.0 (myemail@example.com)"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        weather_data = response.json()
        
        # Format weather data for today or the next few days
        forecast_data = []
        today = parse(weather_data["properties"]["meta"]["updated_at"])
        
        for timeseries in weather_data["properties"]["timeseries"]:
            timestamp = parse(timeseries["time"])
            if today <= timestamp < today + timedelta(days=1):
                details = timeseries["data"]["instant"]["details"]
                temperature = details.get("air_temperature")
                wind_speed = details.get("wind_speed")
                cloud_cover = details.get("cloud_area_fraction")
                precipitation = details.get("precipitation_amount", 0)
                
                # Create a summary of the weather
                forecast_data.append({
                    "date": timestamp.strftime("%Y-%m-%d %H:%M"),
                    "temperature": temperature,
                    "wind_speed": wind_speed,
                    "cloud_cover": cloud_cover,
                    "precipitation": precipitation
                })
        
        # Format into a readable string
        forecast_str = "\n".join([
            f"{day['date']}: {day['temperature']}°C, "
            f"Wind: {day['wind_speed']} m/s, "
            f"Cloud cover: {day['cloud_cover']}%, "
            f"Precipitation: {day['precipitation']} mm"
            for day in forecast_data
        ])
        return forecast_str
    else:
        return "Could not retrieve weather data at this time."



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
                similarities.append((similarity,entry))
                if similarity > highest_similarity:
                    highest_similarity = similarity
                    best_match = entry
                    

    # Sort by similarity score and pick top 5
    similarities.sort(reverse=True, key=lambda x: x[0])
    similarities = similarities[:5]
    # Return the best match (you can return more if needed)
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
synlig_chat_history = []
intern_chat_history = []

var = fetch_weather_data()

system_msg = f""" 
    Du er en KI chatbot som planlegger dates i Bergens/Vestlands området. 
    Du svarer kun på norsk (forklarer eventuelt at dette er en begrensning du har ved behov).
    Du prøver så godt som mulig å tilpasse svaret ditt etter spesifiseringen gitt av brukeren.
        
    For at dateplanen skal være så ferdig som mulig larger du en plan med ulike aktiviteter som bør foregå
    sekvensielt, fra den ene forslåtte aktiviteten til den neste. 
    Hvis du får budsjett eller andre behov spesifisert tar du hensyn til dette.  

    Du kan også etterspørre dagen i uka daten planlegges og justere for dette, eksempeler på justeringer er
    forslag uteliv (bar/resturant) på fredag/lørdag, eller turer/heldagsaktiviteter i helgene. Dette er derimot 
    sekundært til ønskene gitt av brukeren. 

    For de kommende 7 dagene er det også følgende værmelding hentet fra YR: {var}. 
    Nevn gjerne kort om det er spesielle behov for bekledning.
    """
intern_chat_history.append({"role": "system", "content": [{"type" : "text", "text" : system_msg}]})

def ChatWithGPT(user_input):
    #Embedding
    best_matches = find_best_match(user_input, bergen_embedding_data)

    if best_matches: 
        synlig_chat_history.append({"role": "user", "content": [{"type" : "text", "text" : user_input}] })
        updated_user_input = ny_promt_med_forslag(user_input, best_matches)
        intern_chat_history.append({"role": "user", "content": [{"type" : "text", "text" : updated_user_input}] })
    else: 
        synlig_chat_history.append({"role": "user", "content": [{"type" : "text", "text" : user_input}] })
        intern_chat_history.append({"role": "user", "content": [{"type" : "text", "text" : user_input}] })

    # Generate a response from the model
    response = openai.chat.completions.create(
        model=GPT_model,
        messages=intern_chat_history
    )
    
    # Extract the assistant's reply text
    reply = response.choices[0].message.content
    
    # Add assistant's reply to the chat history
    intern_chat_history.append({"role": "assistant", "content": [{"type" : "text", "text" : reply}]})
    synlig_chat_history.append({"role": "assistant", "content": [{"type" : "text", "text" : reply}]})
    
    return reply

# Gradio interface setup
with gr.Blocks() as demo:
    gr.Markdown("# KI bot spesialisert for å gi forslag til en date i Bergen by")
    chat = gr.Chatbot(type="messages")
    #msg = gr.Textbox(show_label=False, placeholder="Fortell dine ønsker for å utforme den beste daten mulig!")

    # Endre stilene til tekstboksen
    msg = gr.Textbox(
        show_label=False,
        placeholder="Fortell dine ønsker for å utforme den beste daten mulig!",
    )

    def submit_message(user_input, synlig_chat_history):
        reply = ChatWithGPT(user_input)
        synlig_chat_history = synlig_chat_history + [{"role": "user", "content": user_input}, 
                                                     {"role": "assistant", "content": reply}]
        return synlig_chat_history, ""
    msg.submit(submit_message, [msg, chat], [chat, msg])
    
demo.launch(debug=True)

