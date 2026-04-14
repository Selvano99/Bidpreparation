"""
Generatore di brochure PDF da template HTML/Jinja2.
Usato per gli item privi di scheda tecnica scaricabile.
"""

import re
import logging
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS

import config

log = logging.getLogger(__name__)

_jinja_env = Environment(
    loader=FileSystemLoader(Path(config.TEMPLATE_FILE).parent),
    autoescape=True
)


def _parse_specs(raw: str) -> tuple[dict | None, str]:
    """
    Prova a interpretare le specifiche come coppie 'Chiave: Valore'.
    Se più del 40% delle righe ha questo formato, restituisce un dict.
    Altrimenti restituisce (None, raw).
    """
    if not raw or str(raw).strip() in ("nan", "None", ""):
        return None, ""

    raw = str(raw).strip()
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    structured = {}
    matched = 0

    for line in lines:
        # Supporta "Chiave: Valore" e "Chiave = Valore"
        m = re.match(r"^(.+?)\s*[:=]\s*(.+)$", line)
        if m:
            structured[m.group(1).strip()] = m.group(2).strip()
            matched += 1

    if lines and matched / len(lines) >= 0.4:
        return structured, raw
    return None, raw


def generate_brochure(item: dict, is_draft: bool = False) -> str | None:
    """
    Genera un PDF per un singolo item.

    Args:
        item: dict con campi del config (item_number, tech_specs, ecc.)
        is_draft: se True aggiunge watermark "BOZZA"

    Returns:
        Path del file generato, oppure None in caso di errore.
    """
    item_number = str(item.get("item_number", "")).strip()
    if not item_number:
        log.warning("Item senza numero, skip.")
        return None

    raw_specs = str(item.get("tech_specs", "")).strip()
    specs_structured, specs_text = _parse_specs(raw_specs)

    safe_item = re.sub(r"[^\w\-]", "_", item_number)
    dest = Path(config.OUTPUT_GENERATED) / f"{safe_item}.pdf"

    template = _jinja_env.get_template(Path(config.TEMPLATE_FILE).name)
    html_content = template.render(
        item_number=item_number,
        description=item.get("description") or item.get("tech_specs", "")[:80],
        manufacturer=item.get("manufacturer", ""),
        model=item.get("model", ""),
        quantity=item.get("quantity", ""),
        tech_specs=specs_text or raw_specs,
        specs_structured=specs_structured,
        notes=item.get("notes", ""),
        gara_name=config.GARA_NAME,
        company_name=config.COMPANY_NAME,
        primary_color=config.PRIMARY_COLOR,
        accent_color=config.ACCENT_COLOR,
        generated_date=date.today().strftime("%d/%m/%Y"),
        is_draft=is_draft,
    )

    try:
        HTML(string=html_content, base_url=str(Path.cwd())).write_pdf(str(dest))
        log.info(f"  [OK] {dest.name}")
        return str(dest)
    except Exception as e:
        log.error(f"  [ERRORE] Item {item_number}: {e}")
        return None


def generate_all(items: list[dict], is_draft: bool = False) -> list[dict]:
    """
    Genera brochure PDF per tutti gli item forniti.

    Args:
        items: lista di dict (output di main.py per item senza scheda scaricata)
        is_draft: aggiunge watermark "BOZZA" a tutti i PDF

    Returns:
        lista di risultati {"item", "status", "path"}
    """
    Path(config.OUTPUT_GENERATED).mkdir(parents=True, exist_ok=True)
    results = []

    for item in items:
        path = generate_brochure(item, is_draft=is_draft)
        results.append({
            "item": item.get("item_number"),
            "status": "generated" if path else "error",
            "path": path,
        })

    return results
