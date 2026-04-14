# Bid Preparation — Gestione Schede Tecniche

Sistema per scaricare e generare schede tecniche per gare d'appalto.

## Setup

```bash
pip install -r requirements.txt
```

> Su Linux potrebbe servire: `sudo apt install libpango-1.0-0 libpangoft2-1.0-0` (dipendenza WeasyPrint)

## Configurazione

Apri `config.py` e adatta:

| Parametro | Descrizione |
|-----------|-------------|
| `COL_ITEM_NUMBER` | Nome colonna item nel tuo Excel |
| `COL_TECH_SPECS` | Nome colonna caratteristiche tecniche |
| `COL_LINK` | Nome colonna con URL scheda tecnica |
| `EXCEL_FILE` | Nome del tuo file Excel |
| `COMPANY_NAME` | Il tuo nome azienda |
| `GARA_NAME` | Titolo della gara |
| `PRIMARY_COLOR` | Colore primario brochure (hex) |

## Utilizzo

```bash
# Elabora tutto il file Excel
python main.py

# Usa un file Excel specifico
python main.py --excel mia_gara.xlsx

# Solo scarica schede dai link (senza generare PDF)
python main.py --only-download

# Solo genera brochure per item senza link
python main.py --only-generate

# Aggiunge watermark "BOZZA" ai PDF generati
python main.py --draft

# Processa solo un item specifico
python main.py --item 042

# Test su primi 10 item
python main.py --limit 10
```

## Test rapidi

```bash
# Crea Excel di esempio
python create_sample_excel.py
python main.py --excel gara_sample.xlsx --draft

# Testa solo il generatore PDF
python test_generator.py
```

## Output

```
output/
├── downloaded/    # Schede tecniche scaricate dai link
│   └── 001.pdf
├── generated/     # Brochure generate da zero
│   └── 002.pdf
└── report.json    # Report completo con esiti per ogni item
```

## Logica di funzionamento

1. **Item con link** → tenta il download diretto
   - Se l'URL è direttamente un PDF/DOCX → scarica
   - Se è una pagina web → cerca link PDF nella pagina (cerca parole chiave: datasheet, scheda tecnica, download, ecc.)
   - Se il download fallisce → genera brochure da template

2. **Item senza link** → genera brochure PDF dal template

3. Il template HTML (`templates/brochure.html`) è personalizzabile e rileva automaticamente se le specifiche tecniche sono in formato `Chiave: Valore` (tabella) o testo libero.
