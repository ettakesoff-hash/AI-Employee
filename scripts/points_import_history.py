"""
points_import_history.py — One-time historical data import

Imports historical promotion data from:
1. Estelle's existing Google Sheet (2024 daily bonus data)
2. All AwardWallet + OMAAT programme pages (full history)

Run once during setup: python scripts/points_import_history.py
"""

import os
import re
import logging
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Import scraper utilities
from points_scraper import (
    PROGRAMMES, SHEET_HEADERS,
    get_spreadsheet, ensure_sheet_structure, write_promotions_to_sheet,
    fetch_awardwallet_programme, fetch_omaat_programme,
    parse_date_flexible, cents_to_cost_per_1000, extract_bonus_pct,
)

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Import from Estelle's 2024 Google Sheet
# ─────────────────────────────────────────────

# Programme column mapping in the source sheet
# Based on what we found: Avianca, Aeroplan, United, Virgin Atlantic,
# Flying Blue, Alaska, American, BA Avios, Qatar, Finnair, Iberia
SOURCE_SHEET_COLUMN_MAP = {
    0: "lifemiles",       # Avianca Lifemiles
    1: "aeroplan",        # Air Canada Aeroplan
    2: "mileageplus",     # United
    3: "virgin_atlantic", # Virgin Atlantic
    4: "flying_blue",     # Air France-KLM Flying Blue
    5: "alaska",          # Alaska Mileage Plan
    6: "aadvantage",      # American AAdvantage
    7: "ba_avios",        # British Airways Avios
    8: "qatar",           # Qatar Airways
    9: "finnair",         # Finnair Plus
    10: "iberia",         # Iberia Plus
}

SOURCE_SHEET_PROGRAMME_NAMES = {
    "lifemiles": "Avianca LifeMiles",
    "aeroplan": "Air Canada Aeroplan",
    "mileageplus": "United MileagePlus",
    "virgin_atlantic": "Virgin Atlantic Flying Club",
    "flying_blue": "Air France-KLM Flying Blue",
    "alaska": "Alaska Airlines Mileage Plan",
    "aadvantage": "American AAdvantage",
    "ba_avios": "British Airways Avios",
    "qatar": "Qatar Airways Privilege Club",
    "finnair": "Finnair Plus",
    "iberia": "Iberia Plus",
}


def collapse_daily_to_promotions(daily_data):
    """
    Convert daily bonus % rows into promotion periods.
    Groups consecutive days with the same bonus % into a single promotion record.

    daily_data: list of (date_str, programme_id, bonus_pct)
    Returns: list of promotion dicts
    """
    # Group by programme
    by_programme = {}
    for date_str, prog_id, bonus_pct in daily_data:
        if prog_id not in by_programme:
            by_programme[prog_id] = []
        by_programme[prog_id].append((date_str, bonus_pct))

    promotions = []
    for prog_id, days in by_programme.items():
        days.sort(key=lambda x: x[0])

        current_start = None
        current_bonus = None
        current_end = None

        for day_str, bonus_pct in days:
            if not bonus_pct:
                # No promotion on this day
                if current_start and current_bonus:
                    # Close current promotion period
                    promotions.append(_make_promo(prog_id, current_start, current_end, current_bonus))
                current_start = None
                current_bonus = None
                current_end = None
                continue

            if bonus_pct == current_bonus:
                # Extend current period
                current_end = day_str
            else:
                # New promotion or change in bonus
                if current_start and current_bonus:
                    promotions.append(_make_promo(prog_id, current_start, current_end, current_bonus))
                current_start = day_str
                current_bonus = bonus_pct
                current_end = day_str

        # Close final period
        if current_start and current_bonus:
            promotions.append(_make_promo(prog_id, current_start, current_end, current_bonus))

    return promotions


def _make_promo(prog_id, start_date, end_date, bonus_pct_str):
    bonus_pct, discount_type = extract_bonus_pct(str(bonus_pct_str))
    return {
        "programme_id": prog_id,
        "programme_name": SOURCE_SHEET_PROGRAMME_NAMES.get(prog_id, prog_id),
        "start_date": start_date,
        "end_date": end_date,
        "bonus_pct": bonus_pct or "",
        "discount_type": discount_type or str(bonus_pct_str),
        "cost_per_1000pts_usd": "",
        "native_currency": PROGRAMMES.get(prog_id, {}).get("native_currency", "USD"),
        "cost_per_1000pts_native": "",
        "source": "manual_import",
        "notes": "Imported from 2024 tracking sheet",
        "added_date": date.today().isoformat(),
    }


def import_from_source_sheet(source_sheet_id):
    """Import Estelle's 2024 daily tracking sheet and convert to promotion periods."""
    log.info(f"Importing from source sheet: {source_sheet_id}")

    client_scopes = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds_path = Path(__file__).parent.parent / "credentials" / "google-service-account.json"
    creds = Credentials.from_service_account_file(str(creds_path), scopes=client_scopes)
    client = gspread.authorize(creds)

    try:
        source_sheet = client.open_by_key(source_sheet_id)
        ws = source_sheet.get_worksheet(0)
        all_rows = ws.get_all_values()
    except Exception as e:
        log.error(f"Could not open source sheet: {e}")
        log.info("Make sure you've shared the source sheet with your service account email")
        return []

    # Find the header row with programme names (typically row 3, index 2)
    header_row_idx = None
    for i, row in enumerate(all_rows[:5]):
        joined = " ".join(row).lower()
        if any(kw in joined for kw in ["avianca", "aeroplan", "united", "virgin"]):
            header_row_idx = i
            break

    if header_row_idx is None:
        log.warning("Could not find programme header row in source sheet")
        return []

    # Map columns to programme IDs based on header names
    col_map = {}
    header_row = all_rows[header_row_idx]
    for col_idx, cell in enumerate(header_row):
        cell_lower = cell.lower()
        if "avianca" in cell_lower or "lifemile" in cell_lower:
            col_map[col_idx] = "lifemiles"
        elif "aeroplan" in cell_lower or "air canada" in cell_lower:
            col_map[col_idx] = "aeroplan"
        elif "united" in cell_lower:
            col_map[col_idx] = "mileageplus"
        elif "virgin" in cell_lower:
            col_map[col_idx] = "virgin_atlantic"
        elif "flying blue" in cell_lower or "air france" in cell_lower:
            col_map[col_idx] = "flying_blue"
        elif "alaska" in cell_lower:
            col_map[col_idx] = "alaska"
        elif "american" in cell_lower:
            col_map[col_idx] = "aadvantage"
        elif "british airways" in cell_lower or "ba avios" in cell_lower:
            col_map[col_idx] = "ba_avios"
        elif "qatar" in cell_lower:
            col_map[col_idx] = "qatar"
        elif "finnair" in cell_lower:
            col_map[col_idx] = "finnair"
        elif "iberia" in cell_lower:
            col_map[col_idx] = "iberia"

    if not col_map:
        log.warning("Could not map any columns to programme IDs")
        return []

    log.info(f"Mapped columns: {col_map}")

    # Parse daily data rows (after header row)
    daily_data = []
    for row in all_rows[header_row_idx + 1:]:
        if not row or not row[0]:
            continue

        # First column should be a date
        date_str = parse_date_flexible(row[0])
        if not date_str:
            continue

        for col_idx, prog_id in col_map.items():
            if col_idx < len(row) and row[col_idx].strip():
                bonus_val = row[col_idx].strip()
                # Filter out non-bonus values
                if re.search(r"\d", bonus_val):  # must contain a digit
                    daily_data.append((date_str, prog_id, bonus_val))

    log.info(f"Found {len(daily_data)} daily data points")

    promotions = collapse_daily_to_promotions(daily_data)
    log.info(f"Collapsed into {len(promotions)} promotion periods")
    return promotions


# ─────────────────────────────────────────────
# Full Historical Import
# ─────────────────────────────────────────────

def run_full_historical_import():
    """
    Import ALL historical data:
    1. Scrape every AwardWallet + OMAAT programme page (full history)
    2. Import Estelle's 2024 tracking sheet
    """
    spreadsheet = get_spreadsheet()
    ws = ensure_sheet_structure(spreadsheet)

    all_promotions = []

    # Step 1: Scrape all web sources
    import time
    log.info("=== Step 1: Scraping web sources ===")
    for prog_id, prog in PROGRAMMES.items():
        try:
            if prog["source"] == "awardwallet":
                promos = fetch_awardwallet_programme(prog_id, prog)
                all_promotions.extend(promos)
                time.sleep(2)
                # Also scrape OMAAT secondary source for start dates
                if prog.get("omaat_url"):
                    log.info(f"  Also scraping OMAAT for start dates: {prog_id}")
                    omaat_prog = dict(prog)
                    omaat_prog["url"] = prog["omaat_url"]
                    omaat_promos = fetch_omaat_programme(prog_id, omaat_prog)
                    all_promotions.extend(omaat_promos)
                    time.sleep(2)
            elif prog["source"] == "onemileatatime":
                promos = fetch_omaat_programme(prog_id, prog)
                all_promotions.extend(promos)
                time.sleep(2)
            else:
                continue
        except Exception as e:
            log.error(f"Error scraping {prog_id}: {e}")

    # Step 2: Import 2024 source sheet
    log.info("=== Step 2: Importing 2024 tracking sheet ===")
    source_sheet_id = os.environ.get(
        "SOURCE_SHEET_ID",
        "1VoKcXQpp3Oo5g5OegoiZ0kkBf75CV1qQ9WN9NSnwZ_Q"  # Estelle's 2024 sheet
    )
    source_promos = import_from_source_sheet(source_sheet_id)
    all_promotions.extend(source_promos)

    # Step 3: Write everything
    log.info(f"=== Step 3: Writing {len(all_promotions)} total records ===")
    added = write_promotions_to_sheet(ws, all_promotions)
    log.info(f"Import complete. {added} new records written to Google Sheets.")


if __name__ == "__main__":
    run_full_historical_import()
