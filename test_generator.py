"""
Test rapido del generatore PDF senza bisogno del file Excel.
Genera una brochure di esempio con dati fittizi.

Uso: python test_generator.py
"""

from pathlib import Path
import config, generator

# Assicurati che la cartella output esista
Path(config.OUTPUT_GENERATED).mkdir(parents=True, exist_ok=True)

sample_item = {
    "item_number": "TEST-001",
    "description": "Pompa centrifuga industriale multistadio",
    "tech_specs": (
        "Portata: 150 m³/h\n"
        "Prevalenza: 40 mca\n"
        "Potenza motore: 15 kW\n"
        "Velocità: 2900 rpm\n"
        "Materiale corpo: ghisa EN-GJL-250\n"
        "Materiale girante: acciaio inox AISI 316\n"
        "Grado protezione: IP55\n"
        "Classe isolamento: F\n"
        "Connessioni: DN65/DN50 flangiato PN16\n"
        "Temperatura fluido: -10 ÷ +120 °C\n"
        "Peso: 87 kg"
    ),
    "manufacturer": "Grundfos",
    "model": "CM15-4 AVBE",
    "quantity": "2 pz",
    "notes": "Verificare disponibilità a magazzino. Richiedere curva caratteristica.",
}

print("Generazione brochure di test...")
path = generator.generate_brochure(sample_item, is_draft=True)

if path:
    print(f"Brochure generata: {path}")
else:
    print("Errore durante la generazione.")
