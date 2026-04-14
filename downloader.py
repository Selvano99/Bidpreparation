"""
Scansione URL e download schede tecniche.
Supporta download diretto (PDF/DOCX) e scraping pagine web con link PDF.
"""

import asyncio
import os
import re
import logging
from pathlib import Path
from urllib.parse import urlparse, urljoin

import aiohttp
from bs4 import BeautifulSoup
from tqdm.asyncio import tqdm_asyncio

import config

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger(__name__)

HEADERS = {"User-Agent": config.USER_AGENT}


def _safe_filename(item_number: str, url: str, content_type: str = "") -> str:
    """Genera un nome file sicuro basato su item number + estensione rilevata."""
    safe_item = re.sub(r"[^\w\-]", "_", str(item_number))
    ext = ""
    parsed = urlparse(url)
    url_path = parsed.path.lower()
    for e in config.DIRECT_EXTENSIONS:
        if url_path.endswith(e):
            ext = e
            break
    if not ext:
        if "pdf" in content_type:
            ext = ".pdf"
        elif "word" in content_type or "docx" in content_type:
            ext = ".docx"
        elif "excel" in content_type or "xlsx" in content_type:
            ext = ".xlsx"
        else:
            ext = ".pdf"  # fallback
    return f"{safe_item}{ext}"


def _is_direct_file(url: str) -> bool:
    """True se l'URL punta direttamente a un file scaricabile."""
    path = urlparse(url).path.lower()
    return any(path.endswith(ext) for ext in config.DIRECT_EXTENSIONS)


async def _find_pdf_link(session: aiohttp.ClientSession, page_url: str) -> str | None:
    """
    Visita una pagina web e cerca link a PDF (scheda tecnica, datasheet, ecc.).
    Restituisce il primo URL trovato o None.
    """
    keywords = [
        "datasheet", "scheda tecnica", "technical", "brochure",
        "specification", "spec", "catalogue", "catalogo", "download"
    ]
    try:
        async with session.get(page_url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=config.DOWNLOAD_TIMEOUT)) as resp:
            if resp.status != 200:
                return None
            html = await resp.text(errors="ignore")
    except Exception:
        return None

    soup = BeautifulSoup(html, "lxml")
    candidates = []

    for tag in soup.find_all("a", href=True):
        href = tag["href"].lower()
        text = tag.get_text(strip=True).lower()
        # Priorità 1: link diretto a PDF
        if href.endswith(".pdf"):
            score = sum(1 for kw in keywords if kw in href or kw in text)
            candidates.append((score + 10, tag["href"]))
        # Priorità 2: testo del link contiene keywords
        elif any(kw in text for kw in keywords):
            candidates.append((sum(1 for kw in keywords if kw in text), tag["href"]))

    if not candidates:
        return None

    candidates.sort(reverse=True)
    best_href = candidates[0][1]
    # Risolvi URL relativo
    return urljoin(page_url, best_href)


async def _download_file(
    session: aiohttp.ClientSession,
    url: str,
    dest_path: Path,
    item_number: str
) -> dict:
    """Scarica un file e lo salva. Restituisce dizionario con risultato."""
    result = {"item": item_number, "url": url, "status": "error", "path": None}

    for attempt in range(1, config.RETRY_ATTEMPTS + 1):
        try:
            async with session.get(
                url, headers=HEADERS,
                timeout=aiohttp.ClientTimeout(total=config.DOWNLOAD_TIMEOUT)
            ) as resp:
                if resp.status != 200:
                    result["error"] = f"HTTP {resp.status}"
                    continue

                content_type = resp.headers.get("Content-Type", "")
                filename = _safe_filename(item_number, url, content_type)
                filepath = dest_path / filename

                content = await resp.read()
                if len(content) < 1000:  # file troppo piccolo, probabilmente errore
                    result["error"] = "File troppo piccolo (probabile pagina errore)"
                    continue

                filepath.write_bytes(content)
                result["status"] = "ok"
                result["path"] = str(filepath)
                return result

        except asyncio.TimeoutError:
            result["error"] = f"Timeout (tentativo {attempt})"
        except Exception as e:
            result["error"] = str(e)

    return result


async def _process_item(
    session: aiohttp.ClientSession,
    item: dict,
    dest_path: Path,
    semaphore: asyncio.Semaphore
) -> dict:
    """Processa un singolo item: determina URL scaricabile e lo scarica."""
    async with semaphore:
        url = str(item.get("url", "")).strip()
        item_number = item.get("item_number", "unknown")

        if not url or url in ("nan", "None", ""):
            return {"item": item_number, "status": "no_url", "url": None, "path": None}

        # Se l'URL punta direttamente a un file
        if _is_direct_file(url):
            return await _download_file(session, url, dest_path, item_number)

        # Altrimenti prova a cercare un PDF nella pagina
        pdf_url = await _find_pdf_link(session, url)
        if pdf_url:
            return await _download_file(session, pdf_url, dest_path, item_number)

        return {
            "item": item_number, "status": "not_found",
            "url": url, "path": None,
            "error": "Nessun PDF trovato nella pagina"
        }


async def download_all(items: list[dict]) -> list[dict]:
    """
    Scarica schede tecniche per tutti gli item con URL.

    Args:
        items: lista di dict con chiavi 'item_number' e 'url'

    Returns:
        lista di risultati per ogni item
    """
    dest_path = Path(config.OUTPUT_DOWNLOADED)
    dest_path.mkdir(parents=True, exist_ok=True)

    semaphore = asyncio.Semaphore(config.MAX_CONCURRENT)
    connector = aiohttp.TCPConnector(ssl=False, limit=config.MAX_CONCURRENT)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [
            _process_item(session, item, dest_path, semaphore)
            for item in items
        ]
        results = await tqdm_asyncio.gather(
            *tasks,
            desc="Download schede tecniche",
            colour="green"
        )

    return list(results)


def run_downloads(items: list[dict]) -> list[dict]:
    """Entry point sincrono per il download."""
    return asyncio.run(download_all(items))
