"""
Script di supporto: crea un file Excel di esempio con la struttura attesa.
Utile per testare il sistema prima di usare il file reale.

Uso: python create_sample_excel.py
"""

import pandas as pd

data = {
    "Item": ["001", "002", "003", "004", "005"],
    "Descrizione": [
        "Pompa centrifuga industriale",
        "Quadro elettrico BT",
        "Valvola a sfera DN50",
        "Motore elettrico asincrono",
        "Filtro aria industriale",
    ],
    "Caratteristiche Tecniche": [
        "Portata: 150 m³/h\nPrevalenza: 40 mca\nPotenza: 15 kW\nMateriale corpo: ghisa\nGrado protezione: IP55",
        "Tensione: 400V AC\nCorrente nominale: 250A\nGrado protezione: IP54\nDimensioni: 800x600x250mm",
        "DN: 50mm\nPN: 16 bar\nMateriale: acciaio inox 316L\nTemperatura max: 180°C\nConnesione: filettata",
        "Potenza: 7.5 kW\nVelocità: 1450 rpm\nTensione: 400V\nFrequenza: 50 Hz\nGrado protezione: IP65",
        "Portata aria: 2000 m³/h\nEfficienza filtraggio: F7\nPerdita di carico: 150 Pa\nClasse fuoco: M1",
    ],
    "Produttore": ["Grundfos", "Schneider", "Watts", "ABB", "Camfil"],
    "Modello": ["CM15-4", "Prisma Plus", "BA", "M2AA112M", "FARR 30/30"],
    "Quantità": ["2", "1", "8", "3", "4"],
    "Link": [
        "https://product-selection.grundfos.com/products/cm",  # link web generico
        "",  # nessun link → verrà generata brochure
        "",  # nessun link → verrà generata brochure
        "https://new.abb.com/motors-generators",               # link web generico
        "",  # nessun link → verrà generata brochure
    ],
}

df = pd.DataFrame(data)
df.to_excel("gara_sample.xlsx", index=False)
print("File creato: gara_sample.xlsx")
print("Colonne:", list(df.columns))
print(f"Righe: {len(df)}")
