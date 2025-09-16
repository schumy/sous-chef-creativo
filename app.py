# app.py
#--- IL SUO COMPITO è SOLO QUELLO DI DISEGNARE L'INTERFACCIA CON STREAMLIT ---
#---!!! QUALSIASI PULSANTE PREMUTO QUA SERVIRà A CHIAMARE UNA FUNZIONE DI ALOGIC_MANAGER.PY !!!---
import streamlit as st
import api_clients as ac
import logic_manager as lm
import api_clients as ac
import os
import json

if 'lista_da_confermare' not in st.session_state:
    st.session_state.lista_da_confermare = None
if 'file_processato_id' not in st.session_state:
    st.session_state.file_processato_id = None
# --- Creazione della cartella temporanea (se non esiste) ---
TEMP_DIR = "temp_uploads"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# --- 1. Inizializzazione della Memoria ---
# Controlliamo se la lista 'ingredienti' non è ancora nella memoria della sessione.
# Se non c'è, la creiamo come una lista vuota.
# Questo blocco di codice viene eseguito solo la PRIMA volta che l'app parte.
if 'ingredienti' not in st.session_state:
    st.session_state.ingredienti = []

if 'dispensa' not in st.session_state:
    st.session_state.dispensa = lm.carica_dispensa()

# --- Interfaccia Utente ---
st.title("🍳 Sous-Chef Creativo")
st.write("Aggiungi gli ingredienti che hai in frigo e ti suggerirò cosa cucinare!")

st.subheader("🛒 Inizia da qui: Carica lo scontrino")

uploaded_file = st.file_uploader(
    "Seleziona un'immagine dello scontrino", 
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    #creazione di un id univoco per il file
    file_id = f"{uploaded_file.name}-{uploaded_file.size}"

    # Controlliamo se non abbiamo già elaborato questo file
    if file_id != st.session_state.get('file_processato_id'):

        #salva il file caricato in una cartella temporanea
        temp_file_path = os.path.join(TEMP_DIR, uploaded_file.name)
        with open(temp_file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
       
        with st.spinner("Lettura testo scontrino... A breve la lista degli ingredienti!"):
            #usiamo la funzione dal client api
            testo_grezzo = ac.estrai_testo_da_scontrino(temp_file_path)
            if testo_grezzo:
                # Salviamo la lista pulita NELLO STATO DI SESSIONE
                st.session_state.lista_da_confermare = ac.pulisci_lista_ingredienti_con_ia(testo_grezzo)
                st.session_state.file_processato_id = file_id
            else:
                st.error("Impossibile leggere dallo scontrino.")
                st.session_state.lista_da_confermare = []   #lista vuota in caso di errore
            #temporaneamente lo utilizzo come set così da non avere duplicati

if st.session_state.lista_da_confermare is not None:
    
    st.info("Scontrino letto! Rimuovi eventuali errori e conferma cosa aggiungere alla dispensa.")

    with st.form("form_conferma"):
        ingredienti_selezionati = st.multiselect(
            "Ingredienti da aggiungere:",
            options=st.session_state.lista_da_confermare,
            default=st.session_state.lista_da_confermare  # Tutti preselezionati
        ) 
        
        conferma = st.form_submit_button('Aggiungi alla lista.')
        if conferma:
            for alimento in ingredienti_selezionati:
                    lm.aggiungi_ingrediente(st.session_state.dispensa, alimento)
                    lm.salva_dispensa(st.session_state.dispensa)
            st.success(f"Aggiunti {len(ingredienti_selezionati)} ingredienti alla dispensa!")

            #resettiamo lo stato      
            st.session_state.lista_da_confermare = None
            st.rerun()

st.write("---") # Separatore

# --- 2. Form per Aggiungere Ingredienti ---
# Usiamo un 'form' per raggruppare l'input e il pulsante di aggiunta.
# Il codice al suo interno viene eseguito solo quando il 'submit_button' viene premuto.
with st.form(key="form_ingredienti", clear_on_submit=True):
    # Il text_input per un nuovo ingrediente
    nuovo_ingrediente = st.text_input(
        label="Inserisci un ingrediente:",
        placeholder="Es: Pomodoro",
        key="input_ingrediente" # Una chiave univoca è buona pratica
    )
    
    # Il pulsante per inviare il form
    submitted = st.form_submit_button("Aggiungi Ingrediente")

    # Se il pulsante "Aggiungi" è stato premuto E l'utente ha scritto qualcosa...
    if submitted and nuovo_ingrediente:
        successo = lm.aggiungi_ingrediente(st.session_state.dispensa, nuovo_ingrediente)
        
        #gestisce solo la risposta per l'interfaccia
        if not successo:
            st.toast(f"'{nuovo_ingrediente}' è già nella lista!", icon="😉")
        else:
            st.toast(f"'{nuovo_ingrediente}' aggiunto!", icon="✅")
# --- 3. Visualizzazione della Lista Corrente ---
st.write("---") # Una linea di separazione
st.write("**Ingredienti attuali:**")

# Se la lista in memoria non è vuota, la mostriamo.
if not st.session_state.dispensa:
    st.warning("La tua dispensa è vuota.")
else:
    for ingrediente in st.session_state.dispensa[:]:
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            st.info(f"{ingrediente}")
        with col2:
            if st.button("🗑️", key=f"del_{ingrediente}"):
                lm.rimuovi_ingrediente(st.session_state.dispensa, ingrediente)
                st.rerun()
    
    #if st.button("Pulisci Tuta La Lista"):
        #st.session_state.ingredienti = []
        #st.rerun()

st.write("---")

# --- SEZIONE PER IMPORTARE ED ESPORTARE LA DISPENSA ---
with st.expander("📂 Gestisci la tua Dispensa (Importa/Esporta)"):

    # --- IMPORTA ---
    st.subheader("Importa una dispensa")
    file_importato = st.file_uploader(
        "Carica un file 'dispensa.json' per ripristinare i tuoi ingredienti.",
        type="json"
    )
    
    if file_importato is not None:
        # Leggiamo il contenuto del file
        contenuto_stringa = file_importato.getvalue().decode("utf-8")
        # Convertiamo la stringa JSON in una lista Python
        dati_importati = json.loads(contenuto_stringa)
        
        # Aggiorniamo la nostra dispensa in sessione
        st.session_state.dispensa = dati_importati
        
        st.success("Dispensa importata con successo!")
        st.rerun()

    # --- ESPORTA ---
    st.subheader("Esporta la tua dispensa")
    # Mostriamo il pulsante solo se la dispensa non è vuota
    if st.session_state.dispensa:
        # Convertiamo la nostra lista Python in una stringa di testo JSON formattata
        dispensa_json_string = json.dumps(st.session_state.dispensa, indent=4)
        
        st.download_button(
           label="📥 Scarica la Dispensa",
           data=dispensa_json_string,
           file_name='dispensa.json',
           mime='application/json',
        )
    else:
        st.warning("La tua dispensa è vuota. Aggiungi ingredienti per poterla esportare.")


# --- 4. Pulsante per Generare le Ricette ---
st.write("---")
st.subheader("👨‍🍳 Genera le tue ricette!")

# Aggiungiamo un campo di testo per l'ingrediente guida
ingrediente_guida = st.text_input(
    "Vuoi una ricetta basata su un ingrediente specifico? (Opzionale)",
    placeholder="Es: Pollo, Pomodoro..."
)

# In app.py
modalita_creativa = st.checkbox("💡 Modalità Creativa (suggerisci 1-3 ingredienti extra)")

if st.button("Genera Ricette!", disabled=not st.session_state.dispensa):
    # FASE 1: Filtro ingredienti (il nostro "portiere")
    with st.spinner("Controllo gli ingredienti in dispensa..."):
        ingredienti_filtrati = ac.filtra_ingredienti_commestibili(st.session_state.dispensa)
    
    st.info(f"Ricetta generata usando: {', '.join(ingredienti_filtrati)}")
    
    # FASE 2: Generazione ricetta (con la nuova logica)
    with st.spinner("Il nostro chef sta pensando..."):
        # Passiamo sia la lista filtrata SIA l'ingrediente guida (che può essere vuoto)
        ricette = ac.genera_ricette_da_api(
            ingredienti_filtrati,
            ingrediente_guida,
            creativo=modalita_creativa  # Aggiungi questo parametro
            )
        st.markdown("### Ecco cosa puoi preparare:")
        st.success(ricette)
