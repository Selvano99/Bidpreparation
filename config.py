"""
Configurazione centrale: adatta i nomi delle colonne al tuo file Excel.
"""

# --- COLONNE EXCEL ---
# Modifica questi valori con i nomi esatti delle colonne nel tuo Excel
COL_ITEM_NUMBER    = "Item"           # Colonna numero item (es. "Item", "Pos.", "N°")
COL_DESCRIPTION    = "Descrizione"   # Colonna descrizione prodotto
COL_TECH_SPECS     = "Caratteristiche Tecniche"  # Colonna specifiche tecniche
COL_LINK           = "Link"          # Colonna con URL scheda tecnica (vuota se assente)
COL_MANUFACTURER   = "Produttore"    # Colonna produttore (opzionale)
COL_MODEL          = "Modello"       # Colonna modello (opzionale)
COL_QUANTITY       = "Quantità"      # Colonna quantità (opzionale)

# --- PATH ---
EXCEL_FILE         = "gara.xlsx"     # Nome del file Excel (nella root del progetto)
OUTPUT_DOWNLOADED  = "output/downloaded"
OUTPUT_GENERATED   = "output/generated"
TEMPLATE_FILE      = "templates/brochure.html"

# --- DOWNLOAD ---
DOWNLOAD_TIMEOUT   = 20             # Secondi di timeout per ogni download
MAX_CONCURRENT     = 10             # Download paralleli simultanei
RETRY_ATTEMPTS     = 3              # Tentativi in caso di errore
USER_AGENT         = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Estensioni considerate come schede tecniche scaricabili direttamente
DIRECT_EXTENSIONS  = {".pdf", ".docx", ".doc", ".xlsx", ".zip"}

# --- BROCHURE GENERATA ---
COMPANY_NAME       = "Nome Azienda"          # Il tuo nome azienda per il footer
COMPANY_LOGO       = ""                      # Path logo (es. "assets/logo.png"), vuoto = nessuno
GARA_NAME          = "Gara d'Appalto 2025"  # Titolo gara per intestazione
PRIMARY_COLOR      = "#1a3a5c"               # Colore primario (blu scuro default)
ACCENT_COLOR       = "#e8f0fe"               # Colore sfondo card
