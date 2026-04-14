"""
Orchestratore principale.

Uso:
    python main.py                        # Elabora tutto il file Excel
    python main.py --only-download        # Solo scarica schede dai link
    python main.py --only-generate        # Solo genera brochure per item senza link
    python main.py --draft                # Aggiunge watermark "BOZZA" ai PDF generati
    python main.py --item 42              # Processa solo l'item con numero 42
    python main.py --limit 10            # Processa solo i primi 10 item
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import pandas as pd
from colorama import Fore, Style, init as colorama_init

import config
import downloader
import generator

colorama_init(autoreset=True)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger(__name__)


# ────────────────────────────────────────────
# LETTURA EXCEL
# ────────────────────────────────────────────

def load_excel(path: str) -> list[dict]:
    """Legge il file Excel e restituisce lista di dict normalizzati."""
    log.info(f"Carico file Excel: {path}")
    try:
        df = pd.read_excel(path, dtype=str)
    except FileNotFoundError:
        log.error(f"File non trovato: {path}")
        sys.exit(1)

    # Pulizia: rimuovi righe completamente vuote
    df = df.dropna(how="all")

    # Mappa colonne configurate (salta quelle mancanti)
    col_map = {
        "item_number":  config.COL_ITEM_NUMBER,
        "description":  config.COL_DESCRIPTION,
        "tech_specs":   config.COL_TECH_SPECS,
        "url":          config.COL_LINK,
        "manufacturer": config.COL_MANUFACTURER,
        "model":        config.COL_MODEL,
        "quantity":     config.COL_QUANTITY,
    }

    items = []
    for _, row in df.iterrows():
        item = {}
        for key, col_name in col_map.items():
            if col_name in df.columns:
                val = str(row.get(col_name, "")).strip()
                item[key] = "" if val in ("nan", "None") else val
            else:
                item[key] = ""
        items.append(item)

    log.info(f"  {len(items)} item caricati.")
    return items


# ────────────────────────────────────────────
# REPORT
# ────────────────────────────────────────────

def print_report(download_results: list[dict], generate_results: list[dict]):
    ok_dl     = [r for r in download_results if r["status"] == "ok"]
    no_url    = [r for r in download_results if r["status"] == "no_url"]
    err_dl    = [r for r in download_results if r["status"] in ("error", "not_found")]
    ok_gen    = [r for r in generate_results if r["status"] == "generated"]
    err_gen   = [r for r in generate_results if r["status"] == "error"]

    print()
    print("=" * 55)
    print(f"  REPORT FINALE")
    print("=" * 55)
    print(f"  {Fore.GREEN}Schede scaricate:    {len(ok_dl):>4}{Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}Senza link:          {len(no_url):>4}{Style.RESET_ALL}")
    print(f"  {Fore.RED}Errori download:     {len(err_dl):>4}{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}Brochure generate:   {len(ok_gen):>4}{Style.RESET_ALL}")
    print(f"  {Fore.RED}Errori generazione:  {len(err_gen):>4}{Style.RESET_ALL}")
    print("=" * 55)

    if err_dl:
        print(f"\n{Fore.RED}Item con errori download:{Style.RESET_ALL}")
        for r in err_dl:
            print(f"  • Item {r['item']}: {r.get('error','?')} — {r.get('url','')}")

    if err_gen:
        print(f"\n{Fore.RED}Item con errori generazione:{Style.RESET_ALL}")
        for r in err_gen:
            print(f"  • Item {r['item']}")

    # Salva report JSON
    report = {"downloaded": download_results, "generated": generate_results}
    report_path = Path("output/report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\n  Report salvato in: {report_path}")


# ────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Bid Preparation — Gestione schede tecniche")
    parser.add_argument("--only-download", action="store_true", help="Solo scarica dai link")
    parser.add_argument("--only-generate", action="store_true", help="Solo genera brochure")
    parser.add_argument("--draft",         action="store_true", help="Aggiunge watermark BOZZA")
    parser.add_argument("--item",          type=str,            help="Processa solo questo item number")
    parser.add_argument("--limit",         type=int,            help="Limita a N item")
    parser.add_argument("--excel",         type=str,            default=config.EXCEL_FILE)
    args = parser.parse_args()

    # Carica dati
    items = load_excel(args.excel)

    # Filtri
    if args.item:
        items = [i for i in items if i.get("item_number") == args.item]
        if not items:
            log.error(f"Item '{args.item}' non trovato.")
            sys.exit(1)
    if args.limit:
        items = items[:args.limit]

    download_results = []
    generate_results = []

    # Dividi: item con link vs senza
    items_with_url    = [i for i in items if i.get("url")]
    items_without_url = [i for i in items if not i.get("url")]

    # ── DOWNLOAD ──
    if not args.only_generate:
        if items_with_url:
            print(f"\n{Fore.CYAN}→ Download schede tecniche ({len(items_with_url)} item)...{Style.RESET_ALL}")
            download_results = downloader.run_downloads(items_with_url)

            # Gli item il cui download è fallito vanno in generazione
            failed = [
                items_with_url[i] for i, r in enumerate(download_results)
                if r["status"] != "ok"
            ]
            items_without_url.extend(failed)
        else:
            log.info("Nessun item con link da scaricare.")

    # ── GENERAZIONE ──
    if not args.only_download:
        if items_without_url:
            print(f"\n{Fore.CYAN}→ Generazione brochure ({len(items_without_url)} item)...{Style.RESET_ALL}")
            generate_results = generator.generate_all(items_without_url, is_draft=args.draft)
        else:
            log.info("Nessun item da generare.")

    # ── REPORT ──
    print_report(download_results, generate_results)


if __name__ == "__main__":
    main()
