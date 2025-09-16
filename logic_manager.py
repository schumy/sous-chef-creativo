#QUA SONO CONTENUTE LE FUNZIONI CHE GESTISCONO LA LOGICA DELL'APPLICAZIONE

import json
import os # Utile per controllare se il file esiste



def salva_dispensa(dispensa_data):
    NOME_FILE_DISPENSA = "dispensa.json"
    """Salva la lista della dispensa in un file JSON."""
    with open(NOME_FILE_DISPENSA, 'w') as f:
        json.dump(dispensa_data, f, indent=4)

def carica_dispensa():
    NOME_FILE_DISPENSA = "dispensa.json"
    """Carica la lista della dispensa da un file JSON. Se non esiste, restituisce una lista vuota."""
    if os.path.exists(NOME_FILE_DISPENSA):
      try:
        with open(NOME_FILE_DISPENSA, 'r') as f:
          #prova a caricare i dati
          return json.load(f)
        
      except json.JSONDecodeError:
        #se il file è vuoto o corrotto ritorna una lista vuota
        return []
    #se il file non esiste affatto ritorna una lista vuota
    return []

def aggiungi_ingrediente(dispensa_attuale, ingrediente_da_aggiungere):
        if ingrediente_da_aggiungere not in dispensa_attuale:
            # ...aggiungiamo l'ingrediente alla nostra lista in memoria.
            dispensa_attuale.append(ingrediente_da_aggiungere)
            salva_dispensa(dispensa_attuale)
            return True
        return False

def rimuovi_ingrediente(dispensa_attuale, ingrediente_da_rimuovere):
    #Serve a rendere la funzione riutilizzabile anche in altri programmi (+ difensiva)
    if ingrediente_da_rimuovere in dispensa_attuale:
    #Rimuove l'ingrediente dalla dispensa
      dispensa_attuale.remove(ingrediente_da_rimuovere)
      salva_dispensa(dispensa_attuale)
      return True   #operazione riuscita
    
    #Se l'ingrediente non è nella lista non facciamo niente e lo comunichiamo
    return False

