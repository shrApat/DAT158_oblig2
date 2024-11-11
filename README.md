https://huggingface.co/spaces/shrApat/DAT158_olbig2_ML

### Date planlegger for Bergen

Denne nettsiden lar deg bruke KI til å designe din ønskede date i Bergen by! 

Nettsiden er bygd med Gradio og er hostet på hugging face. 


## Repositoriet

- DAT158_oblig_rapport_ML .docx: Rapport for oppgaven
- Date_GPT_deployed.py: Hoved scriptet som utfører date planleggingen og lager en Gradio interface
- Embedd_data.py: Scriptet som transformerer tekstfilene til en vektordatabase i form av .json fil 
- Data: Inneholder rå filer brukt av hovedprogrammet
  - Bergen_..._.txt: Tekst filer som beskriver spisesteder, utesteder og aktiviteter i Bergen
  - bergen_embedded_data.json: Datatabell hvor OpenAi sin embedding moddel har blitt kjørt på txt-filene for å repsentere de i vektor form
- Teste_script: mappe med ulike script brukt i utviklingsprossesen
  - Date_terminal_GPT.py: Tidlig løsning der man kommuniserer med LLM modellen rett inn i terminalen
  - ustende.css: Fil brukt for å forsøke å redigere utsende på Gradio applikasjonen (Dette var misslykket)
  - weather.py: Fil for å teste bruken av YR sin "Location Finder"

## For å lage din egen versjon

1. Generer din egen API key fra Open Ai. Lagre den som en tekst fil eller enviorment variable (gjort på Hugging face spaces)
2. Gjør eventuelle endringer på tekstfilene om ønsket
3. Kjør Embedd_data.py for å ha en oppdatert versjon av .json filen for modellen
4. Kjør Date_GPT_deployed for å starte nettsiden
