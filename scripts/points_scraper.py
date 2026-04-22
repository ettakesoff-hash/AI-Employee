"""
points_scraper.py — Airline Points Promotions Scraper

Scrapes AwardWallet and OneMilleAtATime for current and historical
promotion data, then writes to Google Sheets.

Run daily (or manually): python scripts/points_scraper.py
"""

import os
import re
import time
import json
import logging
from datetime import datetime, date
from pathlib import Path

import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Programme Registry
# Add new programmes here + a row in the Sheets `programmes` tab
# ─────────────────────────────────────────────
PROGRAMMES = {
    # ── AwardWallet ──────────────────────────────────────────────────────────
    "alaska": {
        "name": "Alaska Airlines Mileage Plan",
        "alliance": "Oneworld",
        "native_currency": "USD",
        "source": "awardwallet",
        "url": "https://awardwallet.com/airlines/alaska-atmos-rewards/buy-alaska-miles/",
    },
    "aeroplan": {
        "name": "Air Canada Aeroplan",
        "alliance": "Star Alliance",
        "native_currency": "CAD",
        "source": "awardwallet",
        "url": "https://awardwallet.com/airline-programs/air-canada-aeroplan/buy-points/",
        "omaat_url": "https://onemileatatime.com/deals/buy-air-canada-aeroplan-points/",
    },
    "lifemiles": {
        "name": "Avianca LifeMiles",
        "alliance": "Star Alliance",
        "native_currency": "USD",
        "source": "awardwallet",
        "url": "https://awardwallet.com/airlines/avianca-lifemiles/buy-lifemiles/",
        "omaat_url": "https://onemileatatime.com/deals/buy-avianca-lifemiles/",
    },
    "connectmiles": {
        "name": "Copa ConnectMiles",
        "alliance": "Star Alliance",
        "native_currency": "USD",
        "source": "awardwallet",
        "url": "https://awardwallet.com/airlines/buy-copa-miles/",
    },
    "mileageplus": {
        "name": "United MileagePlus",
        "alliance": "Star Alliance",
        "native_currency": "USD",
        "source": "awardwallet",
        "url": "https://awardwallet.com/airlines/united-mileageplus/buy-united-miles/",
        "omaat_url": "https://onemileatatime.com/deals/buy-united-mileageplus-miles/",
    },
    "virgin_atlantic": {
        "name": "Virgin Atlantic Flying Club",
        "alliance": "SkyTeam",
        "native_currency": "USD",
        "source": "awardwallet",
        "url": "https://awardwallet.com/airlines/virgin-atlantic-flying-club/buy-virgin-points/",
        "omaat_url": "https://onemileatatime.com/deals/buy-virgin-atlantic-flying-club-points/",
    },
    "miles_and_more": {
        "name": "Lufthansa Miles & More",
        "alliance": "Star Alliance",
        "native_currency": "EUR",
        "source": "awardwallet",
        "url": "https://awardwallet.com/airlines/buy-lufthansa-miles/",
    },
    "rapid_rewards": {
        "name": "Southwest Rapid Rewards",
        "alliance": "None",
        "native_currency": "USD",
        "source": "awardwallet",
        "url": "https://awardwallet.com/airlines/southwest-rapid-rewards/buy-southwest-points/",
        "omaat_url": "https://onemileatatime.com/deals/buy-southwest-rapid-rewards-points/",
    },
    "trueblue": {
        "name": "JetBlue TrueBlue",
        "alliance": "None",
        "native_currency": "USD",
        "source": "awardwallet",
        "url": "https://awardwallet.com/airlines/jetblue-trueblue/buy-jetblue-points/",
    },
    "aadvantage": {
        "name": "American AAdvantage",
        "alliance": "Oneworld",
        "native_currency": "USD",
        "source": "awardwallet",
        "url": "https://awardwallet.com/airlines/american-aadvantage/buy-american-airlines-miles/",
    },
    "etihad": {
        "name": "Etihad Guest",
        "alliance": "None",
        "native_currency": "USD",
        "source": "awardwallet",
        "url": "https://awardwallet.com/news/airlines/buy-etihad-miles/",
    },
    "skymiles": {
        "name": "Delta SkyMiles",
        "alliance": "SkyTeam",
        "native_currency": "USD",
        "source": "awardwallet",
        "url": "https://awardwallet.com/airlines/delta-skymiles/buy-delta-miles/",
    },
    # ── OneMilleAtATime ───────────────────────────────────────────────────────
    "qatar": {
        "name": "Qatar Airways Privilege Club",
        "alliance": "Oneworld",
        "native_currency": "USD",
        "source": "onemileatatime",
        "url": "https://onemileatatime.com/deals/buy-qatar-airways-privilege-club-avios/",
    },
    "flying_blue": {
        "name": "Air France-KLM Flying Blue",
        "alliance": "SkyTeam",
        "native_currency": "EUR",
        "source": "onemileatatime",
        "url": "https://onemileatatime.com/deals/buy-air-france-klm-flying-blue-miles/",
    },
    "finnair": {
        "name": "Finnair Plus",
        "alliance": "Oneworld",
        "native_currency": "EUR",
        "source": "onemileatatime",
        "url": "https://onemileatatime.com/deals/buy-finnair-plus-avios/",
    },
    "iberia": {
        "name": "Iberia Plus",
        "alliance": "Oneworld",
        "native_currency": "EUR",
        "source": "onemileatatime",
        "url": "https://onemileatatime.com/deals/buy-iberia-plus-avios/",
    },
    "emirates": {
        "name": "Emirates Skywards",
        "alliance": "None",
        "native_currency": "USD",
        "source": "onemileatatime",
        "url": "https://onemileatatime.com/deals/buy-emirates-skywards-miles/",
    },
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


# ─────────────────────────────────────────────
# Google Sheets Connection
# ─────────────────────────────────────────────

def get_sheets_client():
    scopes = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds_path = Path(__file__).parent.parent / "credentials" / "google-service-account.json"
    creds = Credentials.from_service_account_file(str(creds_path), scopes=scopes)
    return gspread.authorize(creds)


def get_spreadsheet():
    client = get_sheets_client()
    sheet_id = os.environ["GOOGLE_SHEET_ID"]
    return client.open_by_key(sheet_id)


# ─────────────────────────────────────────────
# Parsing Helpers
# ─────────────────────────────────────────────

def cents_to_cost_per_1000(cents_str):
    """Convert '1.47¢' or '1.47' to float cost per 1000 points in that currency."""
    if not cents_str:
        return None
    cleaned = re.sub(r"[¢$£€,\s]", "", str(cents_str))
    try:
        cents = float(cleaned)
        # If it looks like it's already in dollars (e.g. 0.0147), convert
        if cents < 0.1:
            cents = cents * 100
        return round(cents * 10, 2)  # cents per point × 10 = cost per 1000 pts
    except ValueError:
        return None


def parse_date_flexible(date_str):
    """Parse various date formats to YYYY-MM-DD string."""
    if not date_str:
        return None
    date_str = str(date_str).strip()
    formats = [
        "%B %d, %Y",   # March 31, 2026
        "%b %d, %Y",   # Mar 31, 2026
        "%m/%d/%Y",    # 03/31/2026
        "%Y-%m-%d",    # 2026-03-31
        "%d/%m/%Y",    # 31/03/2026
        "%B %Y",       # March 2026
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def extract_bonus_pct(text):
    """Extract percentage from strings like '70% bonus', 'up to 70% bonus', '50% discount'."""
    if not text:
        return None, None
    text = str(text)
    match = re.search(r"(\d+)%", text)
    if not match:
        return None, text.strip()
    pct = int(match.group(1))
    return pct, text.strip()


# ─────────────────────────────────────────────
# AwardWallet Scraper
# ─────────────────────────────────────────────

def fetch_awardwallet_programme(prog_id, prog):
    """Scrape historical promotion table from an AwardWallet programme page."""
    log.info(f"Fetching AwardWallet: {prog['name']}")
    try:
        resp = requests.get(prog["url"], headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        log.warning(f"Failed to fetch {prog['url']}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    promotions = []

    # Find all tables on the page
    tables = soup.find_all("table")
    for table in tables:
        headers_row = table.find("tr")
        if not headers_row:
            continue
        col_headers = [th.get_text(strip=True).lower() for th in headers_row.find_all(["th", "td"])]

        # Identify table columns
        date_col = None
        bonus_col = None
        cost_col = None

        for i, h in enumerate(col_headers):
            if any(kw in h for kw in ["end", "date", "expir", "through"]):
                if date_col is None:
                    date_col = i
        # Assign bonus/cost cols only to columns not already used as date_col
        for i, h in enumerate(col_headers):
            if i == date_col:
                continue
            if any(kw in h for kw in ["bonus", "discount", "offer", "deal", "max"]):
                if bonus_col is None:
                    bonus_col = i
            if any(kw in h for kw in ["cost", "cent", "price", "¢", "per point", "per mile", "min"]):
                if cost_col is None:
                    cost_col = i

        if date_col is None:
            continue

        rows = table.find_all("tr")[1:]  # skip header
        for row in rows:
            cells = row.find_all(["td", "th"])
            if len(cells) <= date_col:
                continue

            end_date_raw = cells[date_col].get_text(strip=True) if date_col < len(cells) else ""
            bonus_raw = cells[bonus_col].get_text(strip=True) if bonus_col is not None and bonus_col < len(cells) else ""
            cost_raw = cells[cost_col].get_text(strip=True) if cost_col is not None and cost_col < len(cells) else ""

            end_date = parse_date_flexible(end_date_raw)
            if not end_date:
                continue

            bonus_pct, discount_type = extract_bonus_pct(bonus_raw)
            cost_per_1000 = cents_to_cost_per_1000(cost_raw)

            promotions.append({
                "programme_id": prog_id,
                "programme_name": prog["name"],
                "start_date": "",
                "end_date": end_date,
                "bonus_pct": bonus_pct or "",
                "discount_type": discount_type or bonus_raw,
                "cost_per_1000pts_usd": cost_per_1000 if prog["native_currency"] == "USD" else "",
                "native_currency": prog["native_currency"],
                "cost_per_1000pts_native": cost_per_1000 or "",
                "source": "awardwallet",
                "notes": "",
                "added_date": date.today().isoformat(),
            })

    # Also try to get current promotion from page text
    current = extract_awardwallet_current(soup, prog_id, prog)
    if current:
        # Merge if not already in table
        existing_end_dates = {p["end_date"] for p in promotions}
        if current["end_date"] not in existing_end_dates:
            promotions.append(current)

    log.info(f"  Found {len(promotions)} promotions for {prog['name']}")
    return promotions


def extract_awardwallet_current(soup, prog_id, prog):
    """Extract current promotion details from page text/meta."""
    text = soup.get_text()

    # Look for "through [date]" or "expires [date]" or "until [date]"
    end_match = re.search(
        r"(?:through|expires?|until|valid through|ends?)\s+([A-Z][a-z]+ \d{1,2},?\s*\d{4})",
        text, re.IGNORECASE
    )
    # Look for cost per point in text
    cost_match = re.search(r"(\d+\.\d+)[¢¢]\s*per\s*(?:point|mile)", text, re.IGNORECASE)
    bonus_match = re.search(r"(\d+)%\s*(?:bonus|discount)", text, re.IGNORECASE)

    if not end_match:
        return None

    end_date = parse_date_flexible(end_match.group(1))
    if not end_date:
        return None

    cost = cents_to_cost_per_1000(cost_match.group(1)) if cost_match else None
    bonus_pct = int(bonus_match.group(1)) if bonus_match else None
    discount_type = f"{bonus_pct}% bonus" if bonus_pct else "Promotion"

    return {
        "programme_id": prog_id,
        "programme_name": prog["name"],
        "start_date": "",
        "end_date": end_date,
        "bonus_pct": bonus_pct or "",
        "discount_type": discount_type,
        "cost_per_1000pts_usd": cost if prog["native_currency"] == "USD" else "",
        "native_currency": prog["native_currency"],
        "cost_per_1000pts_native": cost or "",
        "source": "awardwallet",
        "notes": "Current promotion",
        "added_date": date.today().isoformat(),
    }


# ─────────────────────────────────────────────
# OneMilleAtATime Scraper
# ─────────────────────────────────────────────

def fetch_omaat_programme(prog_id, prog):
    """Scrape historical deal table from a OneMilleAtATime page."""
    log.info(f"Fetching OMAAT: {prog['name']}")
    try:
        resp = requests.get(prog["url"], headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        log.warning(f"Failed to fetch {prog['url']}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    promotions = []

    # OMAAT deal-history tables have NO header row.
    # Column layout is always: [0] offer description, [1] start date, [2] end date
    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        if len(rows) < 1:
            continue

        # Detect if first row is a header (contains "start"/"end" text) or data
        first_cells = [c.get_text(strip=True) for c in rows[0].find_all(["th", "td"])]
        if len(first_cells) < 3:
            continue

        # Check if first row looks like a header
        first_lower = [c.lower() for c in first_cells]
        has_header = any("start" in c or "end" in c or "date" in c for c in first_lower)
        data_rows = rows[1:] if has_header else rows

        # For OMAAT: col 0 = description, col 1 = start date, col 2 = end date
        for row in data_rows:
            cells = row.find_all(["td", "th"])
            if len(cells) < 3:
                continue

            promo_raw = cells[0].get_text(strip=True)
            start_raw = cells[1].get_text(strip=True)
            end_raw = cells[2].get_text(strip=True)

            start_date = parse_date_flexible(start_raw)
            end_date = parse_date_flexible(end_raw)

            if not end_date:
                continue

            bonus_pct, discount_type = extract_bonus_pct(promo_raw)

            promotions.append({
                "programme_id": prog_id,
                "programme_name": prog["name"],
                "start_date": start_date or "",
                "end_date": end_date,
                "bonus_pct": bonus_pct or "",
                "discount_type": discount_type or promo_raw,
                "cost_per_1000pts_usd": "",
                "native_currency": prog["native_currency"],
                "cost_per_1000pts_native": "",
                "source": "onemileatatime",
                "notes": "",
                "added_date": date.today().isoformat(),
            })

    log.info(f"  Found {len(promotions)} promotions for {prog['name']}")
    return promotions


# ─────────────────────────────────────────────
# Current Promotions (AwardWallet main page)
# ─────────────────────────────────────────────

PROGRAMME_ALIASES = {
    "alaska airlines": "alaska",
    "alaska": "alaska",
    "air canada": "aeroplan",
    "aeroplan": "aeroplan",
    "avianca": "lifemiles",
    "lifemiles": "lifemiles",
    "copa": "connectmiles",
    "connectmiles": "connectmiles",
    "united": "mileageplus",
    "mileageplus": "mileageplus",
    "virgin atlantic": "virgin_atlantic",
    "lufthansa": "miles_and_more",
    "miles & more": "miles_and_more",
    "southwest": "rapid_rewards",
    "rapid rewards": "rapid_rewards",
    "jetblue": "trueblue",
    "trueblue": "trueblue",
    "american airlines": "aadvantage",
    "american": "aadvantage",
    "aadvantage": "aadvantage",
    "etihad": "etihad",
    "delta": "skymiles",
    "skymiles": "skymiles",
    "qatar": "qatar",
    "qatar airways": "qatar",
    "air france": "flying_blue",
    "flying blue": "flying_blue",
    "klm": "flying_blue",
    "finnair": "finnair",
    "iberia": "iberia",
    "emirates": "emirates",
    "british airways": "ba_avios",
    "ba avios": "ba_avios",
}

# Sentinel date for open-ended promotions (no published end date)
OPEN_ENDED_DATE = "2099-12-31"


def fetch_current_promotions():
    """
    Scrape the AwardWallet current promotions page.
    Handles programmes with no published end date (stores as 2099-12-31).
    """
    url = "https://awardwallet.com/news/current-promotions-buy-points-miles/"
    log.info("Fetching AwardWallet current promotions page")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        log.warning(f"Failed to fetch current promotions: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text(separator="\n")
    promotions = []
    today_str = date.today().isoformat()

    # AwardWallet's current promotions table has cols:
    # Programme name | Bonus/discount | Cost per point | End date
    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        if len(rows) < 2:
            continue

        for row in rows[1:]:
            cells = row.find_all(["td", "th"])
            if len(cells) < 2:
                continue
            texts = [c.get_text(strip=True) for c in cells]

            # Identify programme from first cell
            prog_name_raw = texts[0].lower()
            prog_id = None
            for alias, pid in PROGRAMME_ALIASES.items():
                if alias in prog_name_raw:
                    prog_id = pid
                    break
            if not prog_id:
                continue

            prog = PROGRAMMES.get(prog_id, {})

            # Find bonus % in any cell
            bonus_pct, discount_type = None, ""
            cost_per_1000 = None
            end_date = None

            for cell_text in texts[1:]:
                if not bonus_pct:
                    bp, dt = extract_bonus_pct(cell_text)
                    if bp:
                        bonus_pct, discount_type = bp, dt
                if not cost_per_1000 and re.search(r"\d+\.\d+[¢¢]", cell_text):
                    cost_per_1000 = cents_to_cost_per_1000(re.search(r"(\d+\.\d+)", cell_text).group(1))
                if not end_date:
                    parsed = parse_date_flexible(cell_text)
                    if parsed:
                        end_date = parsed

            # If no end date found, check for "no published end date" language
            if not end_date:
                row_text = " ".join(texts).lower()
                if "no" in row_text and ("end" in row_text or "published" in row_text):
                    end_date = OPEN_ENDED_DATE
                elif bonus_pct:
                    # Has a promotion but no end date — treat as open-ended
                    end_date = OPEN_ENDED_DATE

            if not end_date or not bonus_pct:
                continue

            promotions.append({
                "programme_id": prog_id,
                "programme_name": prog.get("name", texts[0]),
                "start_date": today_str,  # First day seen = start date
                "end_date": end_date,
                "bonus_pct": bonus_pct,
                "discount_type": discount_type or f"{bonus_pct}% bonus",
                "cost_per_1000pts_usd": cost_per_1000 if prog.get("native_currency") == "USD" else "",
                "native_currency": prog.get("native_currency", "USD"),
                "cost_per_1000pts_native": cost_per_1000 or "",
                "source": "awardwallet",
                "notes": "Open-ended promo" if end_date == OPEN_ENDED_DATE else "Current promotion",
                "added_date": today_str,
            })
            log.info(f"  Current promo: {prog.get('name', texts[0])} — {discount_type} (ends {end_date})")

    log.info(f"Found {len(promotions)} current promotions on AwardWallet main page")
    return promotions


# ─────────────────────────────────────────────
# Google Sheets Writer
# ─────────────────────────────────────────────

SHEET_HEADERS = [
    "programme_id", "programme_name", "start_date", "end_date",
    "bonus_pct", "discount_type", "cost_per_1000pts_usd",
    "native_currency", "cost_per_1000pts_native",
    "source", "notes", "added_date"
]


def get_or_create_worksheet(spreadsheet, name, rows=1000, cols=20):
    try:
        return spreadsheet.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=name, rows=rows, cols=cols)
        return ws


def ensure_sheet_structure(spreadsheet):
    """Create tabs with headers if they don't exist."""
    # promotions tab
    ws = get_or_create_worksheet(spreadsheet, "promotions")
    existing = ws.get_all_values()
    if not existing or existing[0] != SHEET_HEADERS:
        ws.clear()
        ws.append_row(SHEET_HEADERS)
        log.info("Created promotions tab with headers")

    # current_promos tab — cleared and rewritten daily by scraper
    curr_ws = get_or_create_worksheet(spreadsheet, "current_promos")
    log.info("Ensured current_promos tab exists")

    # programmes tab
    prog_ws = get_or_create_worksheet(spreadsheet, "programmes")
    prog_headers = [
        "programme_id", "programme_name", "alliance", "active",
        "native_currency", "awardwallet_url", "omaat_url"
    ]
    prog_existing = prog_ws.get_all_values()
    if not prog_existing or prog_existing[0] != prog_headers:
        prog_ws.clear()
        prog_ws.append_row(prog_headers)
        for pid, p in PROGRAMMES.items():
            prog_ws.append_row([
                pid, p["name"], p.get("alliance", ""),
                "TRUE", p.get("native_currency", "USD"),
                p["url"] if p["source"] == "awardwallet" else "",
                p["url"] if p["source"] == "onemileatatime" else "",
            ])
        log.info("Created programmes tab")

    # base_prices tab
    bp_ws = get_or_create_worksheet(spreadsheet, "base_prices")
    bp_headers = [
        "programme_id", "programme_name",
        "base_cost_per_1000pts_usd", "native_currency",
        "base_cost_per_1000pts_native", "last_updated", "notes"
    ]
    bp_existing = bp_ws.get_all_values()
    if not bp_existing or bp_existing[0] != bp_headers:
        bp_ws.clear()
        bp_ws.append_row(bp_headers)
        for pid, p in PROGRAMMES.items():
            bp_ws.append_row([
                pid, p["name"], "", p.get("native_currency", "USD"), "", "", "Update manually"
            ])
        log.info("Created base_prices tab — please fill in base prices manually")

    return spreadsheet.worksheet("promotions")


def write_current_promos_to_sheet(spreadsheet, current_promotions):
    """Overwrite the current_promos tab with today's active promotions."""
    ws = spreadsheet.worksheet("current_promos")
    ws.clear()
    ws.append_row(SHEET_HEADERS)
    if current_promotions:
        rows = [[str(p.get(h, "")) for h in SHEET_HEADERS] for p in current_promotions]
        ws.append_rows(rows, value_input_option="USER_ENTERED")
    log.info(f"Wrote {len(current_promotions)} current promotions to current_promos tab")


def write_promotions_to_sheet(ws, new_promotions):
    """Append only promotions not already in the sheet (dedup by programme_id + end_date)."""
    existing = ws.get_all_records()
    existing_keys = {
        (r.get("programme_id", ""), r.get("end_date", ""))
        for r in existing
    }

    rows_to_add = []
    for p in new_promotions:
        key = (p.get("programme_id", ""), p.get("end_date", ""))
        if key not in existing_keys:
            rows_to_add.append([str(p.get(h, "")) for h in SHEET_HEADERS])
            existing_keys.add(key)

    if rows_to_add:
        ws.append_rows(rows_to_add, value_input_option="USER_ENTERED")
        log.info(f"Added {len(rows_to_add)} new promotion records to Sheets")
    else:
        log.info("No new promotions to add — sheet is up to date")

    return len(rows_to_add)


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def run_scraper(programmes=None):
    """
    Daily scraper — uses AwardWallet current promotions page as source of truth.
    Start date = first day the promo appears (dedup by programme_id + end_date
    means subsequent runs won't overwrite it).
    Also checks OMAAT for programmes not covered by AwardWallet.
    """
    spreadsheet = get_spreadsheet()
    ws = ensure_sheet_structure(spreadsheet)

    all_promotions = []

    # Step 1: AwardWallet current promotions page (primary source)
    log.info("=== Fetching AwardWallet current promotions ===")
    try:
        current_promos = fetch_current_promotions()
        all_promotions.extend(current_promos)
        time.sleep(2)
    except Exception as e:
        log.error(f"Error fetching AwardWallet current promotions: {e}")

    # Step 2: OMAAT pages for programmes not on AwardWallet main page
    omaat_programmes = [pid for pid, p in PROGRAMMES.items() if p["source"] == "onemileatatime"]
    aw_covered = {p["programme_id"] for p in all_promotions}

    for prog_id in omaat_programmes:
        if prog_id in aw_covered:
            continue
        prog = PROGRAMMES[prog_id]
        try:
            promos = fetch_omaat_programme(prog_id, prog)
            # Only keep promos with end_date >= today (current/future)
            today_str = date.today().isoformat()
            promos = [p for p in promos if p.get("end_date", "") >= today_str]
            all_promotions.extend(promos)
            time.sleep(2)
        except Exception as e:
            log.error(f"Error scraping {prog_id}: {e}")

    # Write to current_promos (cleared daily — source of truth for dashboard)
    write_current_promos_to_sheet(spreadsheet, all_promotions)

    # Write to promotions (append-only historical log)
    added = write_promotions_to_sheet(ws, all_promotions)
    log.info(f"Scrape complete. {added} new records added to history.")
    return all_promotions


if __name__ == "__main__":
    import sys
    # Optionally pass programme IDs as args: python points_scraper.py virgin_atlantic aeroplan
    target_programmes = sys.argv[1:] if len(sys.argv) > 1 else None
    run_scraper(target_programmes)
