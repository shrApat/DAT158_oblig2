

############################
#Dette er en enkelt script som tester YR sin "location forecast" tjeneste. 
#Det hentes en tabell med 7 dagers prognose av været i Bergen som lagres som en tabell.
#APIen er tilgjenglig ved https://developer.yr.no/featured-products/forecast/
#Enedelig implementasjon er i Date_GPT_deployed.py

#OBS: endelig implemtasjon lagerer ikke en txt fil som dette scriptet men laster 
#tabellen som en variabel som den gir til Chat GPT
###########################

import requests
from datetime import datetime, timedelta
from dateutil.parser import parse
from pathlib import Path

#Find the correct root directory (Assingment 2)
script_dir = Path(__file__).resolve().parent

# Sett opp koordinatene for stedet (Her kitt for bergen)
latitude = "60.39299"
longitude = "5.32415"

# Lag en API-forespørsel
url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={latitude}&lon={longitude}"
headers = {"User-Agent": "KI_date_planlegger_Bergen_studieopg (shrpatil12@gmail.com)"}

response = requests.get(url, headers=headers)

# Sjekk om forespørselen var vellykket
if response.status_code == 200:
    weather_data = response.json()
    
    # Filtrer værdata for de neste 7 dagene
    forecast_data = []
    today = parse(weather_data["properties"]["meta"]["updated_at"])  # Bruk dagens dato fra oppdateringstidspunktet
    
    for timeseries in weather_data["properties"]["timeseries"]:
        timestamp = parse(timeseries["time"])  # Bruk dateutil for å håndtere ISO-formatet med Z
        
        # Sjekk om datoen er innen de neste 7 dagene
        if today <= timestamp < today + timedelta(days=7):
            details = timeseries["data"]["instant"]["details"]
            temperature = details.get("air_temperature")
            wind_speed = details.get("wind_speed")
            cloud_cover = details.get("cloud_area_fraction")
            precipitation = details.get("precipitation_amount", 0)
            
            # Legg til i listen
            forecast_data.append({
                "date": timestamp.strftime("%Y-%m-%d %H:%M"),
                "temperature": temperature,
                "wind_speed": wind_speed,
                "cloud_cover": cloud_cover,
                "precipitation": precipitation
            })
else:
    print("Feil ved henting av data:", response.status_code)

# Lagre dataene i en tekstfil
file_path = script_dir.parent / 'data' /"7_day_forecast.txt"
with open(file_path, "w") as file:
    for day in forecast_data:
        file.write(
            f"{day['date']}: Temperatur: {day['temperature']}°C, "
            f"Vindhastighet: {day['wind_speed']} m/s, "
            f"Skydekke: {day['cloud_cover']}%, "
            f"Nedbør: {day['precipitation']} mm\n"
        )