#CONTIENE SOLO LE FUNZIONI CHE PARLANO CON LE API (genera_ricette, estrai_testo)
import os
import io
from google.cloud import vision
from openai import OpenAI
import json

modello_chat = 'gpt-3.5-turbo'
PROMPT_SISTEMA = "Sei un sous-chef esperto. Ti fornirò una lista di ingredienti, e tu dovrai creare un massimo di 3 ricette utilizzando esclusivamente quegli ingredienti. Specifica chiaramente il nome della ricetta, gli ingredienti usati e i passaggi."
# In api_clients.py

def genera_ricette_da_api_elastico(ingredienti, ingrediente_guida=None, modello='gpt-3.5-turbo'):
    """
    Genera ricette basandosi su una lista di ingredienti.
    Se viene fornito un 'ingrediente_guida', le ricette si concentreranno su quello.
    """
    # Formattiamo la lista di ingredienti per l'IA
    ingredienti_formattati = ", ".join(ingredienti)
    
    # --- COSTRUZIONE DINAMICA DEL PROMPT ---
    if ingrediente_guida and ingrediente_guida.strip() != "":
        # Prompt per la generazione GUIDATA
        prompt_utente = f"""
        Crea delle ricette che abbiano come protagonista principale '{ingrediente_guida}'.
        Puoi usare SOLO ed esclusivamente gli altri ingredienti che trovi in questa lista: {ingredienti_formattati}.
        Se l'ingrediente guida non è nella lista, avvisami e non creare la ricetta.
        """
        PROMPT_SISTEMA = "Sei un sous-chef creativo specializzato in ricette mirate."
    else:
        # Prompt per la generazione SEMPLICE (quello che avevamo prima)
        prompt_utente = f"Crea delle ricette usando SOLO ed esclusivamente questi ingredienti: {ingredienti_formattati}."
        PROMPT_SISTEMA = "Sei un sous-chef esperto nello svuotare il frigo."
        
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Chiave API di OpenAI non trovata.")

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=modello,
            max_tokens=1500,
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA},
                {"role": "user", "content": prompt_utente}
            ]
        )
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Si è verificato un errore durante la generazione della ricetta: {e}"

# In api_clients.py

import os
import json
from openai import OpenAI

# (Assicurati che anche gli altri import come 'io' e 'from google.cloud import vision' siano presenti nel file)

def genera_ricette_da_api(ingredienti, ingrediente_guida=None, creativo=False, modello='gpt-3.5-turbo'):
    """
    Genera proposte di pasto. 
    - Se 'creativo' è True, può suggerire ingredienti extra.
    - Se 'ingrediente_guida' è fornito, si concentra su quello.
    """
    ingredienti_formattati = ", ".join(ingredienti)
    
    # --- Scelta della Modalità e Costruzione del Prompt ---

    if creativo:
        # === MODALITÀ CREATIVA ===
        PROMPT_SISTEMA = "Sei un Executive Chef creativo e pratico. Il tuo compito è creare menu interessanti suggerendo piccole aggiunte."
        
        # Costruiamo il prompt utente pezzo per pezzo
        prompt_utente = f"""
        Organizza una proposta di pasto basandoti principalmente su questa lista di ingredienti: [{ingredienti_formattati}].

        HAI IL PERMESSO di suggerire di aggiungere da 1 a 3 ingredienti di base e comuni (come cipolla, aglio, spezie, olio, farina, limone, ecc.) per completare o migliorare significativamente le ricette.
        """

        if ingrediente_guida and ingrediente_guida.strip() != "":
            prompt_utente += f"\nIl pasto deve, se possibile, ruotare attorno all'ingrediente principale: '{ingrediente_guida}'."

        prompt_utente += """
        La tua proposta deve essere strutturata ESATTAMENTE così:
        **Proposta di Pasto:**
        **Primo:** [Nome ricetta e procedimento]
        **Secondo:** [Nome ricetta e procedimento]
        **Contorno:** [Nome ricetta e procedimento]
        **Ingredienti Usati dalla Dispensa:** [Elenca gli ingredienti della lista che hai usato]
        **Ingredienti Extra Suggeriti:** [Elenca i 1-3 ingredienti extra che suggerisci di acquistare]
        """
    else:
        # === MODALITÀ RIGIDA ===
        PROMPT_SISTEMA = "Sei un sous-chef estremamente preciso, pratico e che non si vergogna di suggerire piatti semplici."

        if ingrediente_guida and ingrediente_guida.strip() != "":
            # Prompt GUIDATO e RIGIDO
            prompt_utente = f"""
            Il mio compito è creare una ricetta usando SOLO ed ESCLUSIVAMENTE una lista di ingredienti fornita.
            L'ingrediente principale richiesto è '{ingrediente_guida}'.
            La lista completa di ingredienti che posso usare è: [{ingredienti_formattati}].
            
            Valuta se è possibile creare una ricetta sensata.
            **Anche preparazioni estremamente semplici che usano solo uno o due ingredienti (come un'insalata o cuocere una bistecca) sono considerate risposte valide e apprezzate.**

            Se non è possibile creare assolutamente nulla, rispondi SOLO con: "Mi dispiace, ma con gli ingredienti a disposizione non è possibile creare una ricetta sensata."
            
            Altrimenti, fornisci una o più ricette strutturate ESATTAMENTE così:
            **Nome Ricetta:** [Nome della ricetta]
            **Ingredienti Usati:** [Elenca SOLO gli ingredienti della lista che hai usato]
            **Procedimento:** [Descrivi i passaggi]

            È di fondamentale importanza non inventare o aggiungere NESSUN ingrediente che non sia esplicitamente nella lista fornita.
            """
        else:
            # Prompt SEMPLICE e RIGIDO
            prompt_utente = f"""
            Il mio compito è creare una ricetta usando SOLO ed ESCLUSIVAMENTE la seguente lista di ingredienti: [{ingredienti_formattati}].

            Valuta se con questi ingredienti è possibile creare una ricetta sensata.
            **Anche preparazioni estremamente semplici che usano solo uno o due ingredienti (come un'insalata o cuocere una bistecca) sono considerate risposte valide e apprezzate.**

            Se non è possibile creare assolutamente nulla, rispondi SOLO con: "Mi dispiace, ma con gli ingredienti a disposizione non è possibile creare una ricetta sensata."

            Altrimenti, fornisci una o più ricette strutturate ESATTAMENTE così:
            **Nome Ricetta:** [Nome della ricetta]
            **Ingredienti Usati:** [Elenca SOLO gli ingredienti della lista che hai usato]
            **Procedimento:** [Descrivi i passaggi]

            È di fondamentale importanza non inventare o aggiungere NESSUN ingrediente che non sia esplicitamente nella lista fornita.
            """

    # --- Esecuzione della Chiamata API ---
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Chiave API di OpenAI non trovata.")

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=modello,
            max_tokens=1500,
            temperature=0.7, # Un po' di creatività ma non troppa
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA},
                {"role": "user", "content": prompt_utente}
            ]
        )
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Si è verificato un errore durante la generazione della ricetta: {e}"

def riconosci_ingredienti_da_immagine(percorso_immagine):
    """
    Prende il percorso di un'immagine, la invia a Google Vision API
    e restituisce una lista di etichette.
    """
    # L'autenticazione avviene in automatico grazie a 'gcloud auth'
    client = vision.ImageAnnotatorClient()

    # Leggiamo il file dell'immagine in memoria
    with io.open(percorso_immagine, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    # Eseguiamo il rilevamento delle etichette (oggetti)
    response = client.object_localization(image=image)
    objects = response.localized_object_annotations
    
    lista_oggetti = list(set(obj.name for obj in objects))
    
    # Controlliamo se ci sono stati errori
    if response.error.message:
        raise Exception(
            '{}\nPer maggiori info, vedi https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    return lista_oggetti

def estrai_testo_da_scontrino(percorso_immagine):
    """
    Usa la funzione Document Text Detection di Google Vision
    per estrarre tutto il testo da un'immagine di uno scontrino.
    """
    try:
        # 1. Creiamo il "cliente", il nostro ponte di comunicazione con Google.
        #    L'autenticazione è automatica grazie a gcloud.
        client = vision.ImageAnnotatorClient()

        # 2. Leggiamo il file dell'immagine dal disco in formato binario ("rb").
        with io.open(percorso_immagine, 'rb') as image_file:
            content = image_file.read()

        # 3. Creiamo un oggetto Immagine che la libreria di Google può capire.
        image = vision.Image(content=content)

        # 4. Qui avviene la magia. Diciamo al client di analizzare la nostra immagine.
        #    Questa è la riga che devi completare.
        response = client.document_text_detection(image=image)   # --- COMPLETA TU: Quale funzione del client usiamo per leggere il testo da un 'documento'? ---

        # 5. Una volta ottenuta la risposta, il testo completo si trova in questa proprietà.
        testo_completo = response.full_text_annotation.text
        
        return testo_completo

    except Exception as e:
        print(f"Errore durante la chiamata a Google Vision: {e}")
        return None # Restituiamo None in caso di errore
    
def pulisci_lista_ingredienti_con_ia(testo_grezzo, modello='gpt-3.5-turbo'):
    """
    Usa un LLM per estrarre una lista di ingredienti pulita dal testo grezzo di uno scontrino.
    """
    # Questo prompt è cruciale. Spiega all'IA il suo ruolo, cosa fare,
    # cosa ignorare e in quale formato restituire la risposta (JSON).
    PROMPT_PULIZIA = """
    Sei un assistente esperto nell'analisi di scontrini della spesa italiani.
    Il tuo unico compito è estrarre i prodotti ALIMENTARI da un testo e restituirli come una lista JSON.
    Ignora completamente prezzi, totali, resti, sconti, indirizzi, Partita IVA, Codice Fiscale, e qualsiasi riga che contenga la parola 'IVA'.
    Se un prodotto ha una descrizione (es. 'LATTE FRESCO P.S.'), mantienila.
    """

    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Chiave API di OpenAI non trovata.")

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=modello,
            # Chiediamo all'IA di rispondere in formato JSON per una facile conversione
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": PROMPT_PULIZIA},
                {"role": "user", "content": f"Ecco il testo dello scontrino, estrai gli ingredienti in una lista JSON con una chiave 'ingredienti':\n\n```{testo_grezzo}```"}
            ]
        )
        
        # Estraiamo la risposta JSON e la convertiamo in un dizionario Python
        risultato_json = json.loads(response.choices[0].message.content)
        
        # Restituiamo solo la lista contenuta nel dizionario
        return risultato_json.get('ingredienti', [])

    except Exception as e:
        print(f"Errore durante la pulizia con l'IA: {e}")
        return [] # Restituisce una lista vuota in caso di errore
    

def filtra_ingredienti_commestibili(lista_da_filtrare, modello='gpt-3.5-turbo'):
    """
    Usa un LLM per filtrare una lista, mantenendo solo gli ingredienti commestibili.
    """
    PROMPT_FILTRO = """
    Sei un esperto di cibo. Il tuo unico compito è analizzare una lista di parole e restituire una nuova lista 
    che contenga SOLO ed esclusivamente i nomi di cibi, bevande o ingredienti commestibili. 
    Rimuovi qualsiasi oggetto non commestibile come spazzolini, dentifrici, detersivi, ecc.
    """
    
    # Convertiamo la lista Python in una stringa semplice per il prompt
    lista_in_stringa = ", ".join(lista_da_filtrare)
    
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Chiave API di OpenAI non trovata.")

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=modello,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": PROMPT_FILTRO},
                {"role": "user", "content": f"Dalla seguente lista, estrai solo gli elementi commestibili e restituiscili in una lista JSON con chiave 'ingredienti_commestibili':\n\n{lista_in_stringa}"}
            ]
        )
        
        risultato_json = json.loads(response.choices[0].message.content)
        return risultato_json.get('ingredienti_commestibili', [])

    except Exception as e:
        print(f"Errore durante il filtraggio con l'IA: {e}")
        return lista_da_filtrare # In caso di errore, restituisce la lista originale
if __name__ == "__main__":
    percorso_scontrino = 'immagini/scontrino_test.jpg' # Usa un tuo scontrino di prova
    
    print("--- 1. ESTRAZIONE TESTO GREZZO ---")
    testo_grezzo = estrai_testo_da_scontrino(percorso_scontrino)
    print(testo_grezzo)
    print("---------------------------------")
    
    if testo_grezzo:
        print("\n--- 2. PULIZIA DELLA LISTA CON IA ---")
        lista_pulita = pulisci_lista_ingredienti_con_ia(testo_grezzo)
        print(lista_pulita)
        print("------------------------------------")