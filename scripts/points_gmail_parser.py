"""
points_gmail_parser.py — Gmail Promotion Email Parser

Connects to up to 2 Gmail accounts via IMAP, searches for airline
loyalty programme promotion emails, and writes new promotions to
Google Sheets.

Run manually or on schedule: python scripts/points_gmail_parser.py

Setup:
  - Enable IMAP in Gmail Settings → See all settings → Forwarding and POP/IMAP
  - Create an App Password: Google Account → Security → App Passwords
  - Add to .env:
      GMAIL_ACCOUNT_1=you@gmail.com
      GMAIL_PASSWORD_1=xxxx-xxxx-xxxx-xxxx
      GMAIL_ACCOUNT_2=second@gmail.com
      GMAIL_PASSWORD_2=xxxx-xxxx-xxxx-xxxx
"""

import os
import re
import imaplib
import email
import logging
from datetime import date, datetime
from email.header import decode_header
from pathlib import Path

from dotenv import load_dotenv

from points_scraper import (
    get_spreadsheet, ensure_sheet_structure, write_promotions_to_sheet,
    parse_date_flexible, extract_bonus_pct, cents_to_cost_per_1000, PROGRAMMES,
)

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Airline email sender patterns
# Add new senders here as you discover them
# ─────────────────────────────────────────────
AIRLINE_SENDER_MAP = {
    # Email domain / sender substring → programme_id
    "virginatlantic": "virgin_atlantic",
    "virgin-atlantic": "virgin_atlantic",
    "flyingclub": "virgin_atlantic",
    "aeroplan": "aeroplan",
    "aircanada": "aeroplan",
    "air-canada": "aeroplan",
    "lifemiles": "lifemiles",
    "avianca": "lifemiles",
    "copaair": "connectmiles",
    "copa.com": "connectmiles",
    "united": "mileageplus",
    "mileageplus": "mileageplus",
    "southwest": "rapid_rewards",
    "rapidrewards": "rapid_rewards",
    "jetblue": "trueblue",
    "trueblue": "trueblue",
    "aa.com": "aadvantage",
    "americanairlines": "aadvantage",
    "aadvantage": "aadvantage",
    "etihad": "etihad",
    "etihadguest": "etihad",
    "alaska": "alaska",
    "alaskaair": "alaska",
    "lufthansa": "miles_and_more",
    "miles-and-more": "miles_and_more",
    "delta": "skymiles",
    "deltaskymiles": "skymiles",
    "qatarairways": "qatar",
    "qrewards": "qatar",
    "airfrance": "flying_blue",
    "flyingblue": "flying_blue",
    "klm": "flying_blue",
    "finnair": "finnair",
    "iberia": "iberia",
    "british-airways": "ba_avios",
    "britishairways": "ba_avios",
    "ba.com": "ba_avios",
    "emirates": "emirates",
    "garuda": "garuda",
    "garudaindonesia": "garuda",
    "aerlingus": "aer_lingus",
}

PROGRAMME_NAMES = {k: v["name"] for k, v in PROGRAMMES.items()}
PROGRAMME_NAMES.update({
    "ba_avios": "British Airways Avios",
    "garuda": "Garuda Indonesia GarudaMiles",
    "aer_lingus": "Aer Lingus Avios",
})

# Keywords that indicate a buy/purchase promotion email
PROMO_KEYWORDS = [
    "buy miles", "buy points", "purchase miles", "purchase points",
    "bonus miles", "bonus points", "% bonus", "% off", "promotion",
    "on sale", "miles on sale", "points on sale", "special offer",
    "limited time", "expires", "through", "until",
]


def decode_str(s):
    """Decode email header string."""
    if isinstance(s, bytes):
        return s.decode("utf-8", errors="ignore")
    parts = decode_header(s)
    return "".join(
        part.decode(enc or "utf-8", errors="ignore") if isinstance(part, bytes) else part
        for part, enc in parts
    )


def get_email_body(msg):
    """Extract plain text body from email message."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    body += part.get_payload(decode=True).decode("utf-8", errors="ignore")
                except Exception:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
        except Exception:
            pass
    return body


def identify_programme(sender, subject):
    """Identify which loyalty programme an email is from."""
    combined = (sender + " " + subject).lower()
    for keyword, prog_id in AIRLINE_SENDER_MAP.items():
        if keyword.lower() in combined:
            return prog_id
    return None


def is_promo_email(subject, body):
    """Check if email is about a points purchase promotion."""
    combined = (subject + " " + body[:500]).lower()
    return any(kw in combined for kw in PROMO_KEYWORDS)


def extract_promo_details(subject, body, prog_id):
    """Extract promotion details from email subject + body."""
    combined = subject + "\n" + body

    # Bonus/discount percentage
    bonus_pct, discount_type = extract_bonus_pct(combined)

    # End date
    end_date_match = re.search(
        r"(?:through|until|expires?|valid\s+(?:through|until)|ends?)\s+"
        r"([A-Z][a-z]+ \d{1,2},?\s*\d{4}|\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2})",
        combined, re.IGNORECASE
    )
    end_date = parse_date_flexible(end_match.group(1)) if (end_match := end_date_match) else None

    # Start date
    start_date_match = re.search(
        r"(?:starting?|from|begins?|effective)\s+"
        r"([A-Z][a-z]+ \d{1,2},?\s*\d{4}|\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2})",
        combined, re.IGNORECASE
    )
    start_date = parse_date_flexible(start_date_match.group(1)) if start_date_match else None

    # Cost per point (cents)
    cost_match = re.search(r"(\d+\.\d+)\s*[¢¢c]\s*per\s*(?:point|mile)", combined, re.IGNORECASE)
    cost_per_1000 = cents_to_cost_per_1000(cost_match.group(1)) if cost_match else None

    prog_info = PROGRAMMES.get(prog_id, {})
    native_currency = prog_info.get("native_currency", "USD")

    return {
        "programme_id": prog_id,
        "programme_name": PROGRAMME_NAMES.get(prog_id, prog_id),
        "start_date": start_date or "",
        "end_date": end_date or "",
        "bonus_pct": bonus_pct or "",
        "discount_type": discount_type or "",
        "cost_per_1000pts_usd": cost_per_1000 if native_currency == "USD" else "",
        "native_currency": native_currency,
        "cost_per_1000pts_native": cost_per_1000 or "",
        "source": "email",
        "notes": f"Subject: {subject[:100]}",
        "added_date": date.today().isoformat(),
    }


# ─────────────────────────────────────────────
# Gmail IMAP Connection
# ─────────────────────────────────────────────

def connect_gmail(email_addr, password):
    """Connect to Gmail via IMAP."""
    mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    mail.login(email_addr, password)
    return mail


def fetch_promo_emails(mail, days_back=365):
    """
    Search inbox for promotion emails from the last N days.
    Returns list of parsed promotion dicts.
    """
    mail.select("inbox")

    # Search for emails with promo keywords in subject
    since_date = (datetime.now().replace(year=datetime.now().year - 1)).strftime("%d-%b-%Y")
    search_terms = [
        f'(SINCE "{since_date}" SUBJECT "bonus")',
        f'(SINCE "{since_date}" SUBJECT "buy miles")',
        f'(SINCE "{since_date}" SUBJECT "buy points")',
        f'(SINCE "{since_date}" SUBJECT "% off")',
        f'(SINCE "{since_date}" SUBJECT "on sale")',
        f'(SINCE "{since_date}" SUBJECT "promotion")',
    ]

    all_email_ids = set()
    for term in search_terms:
        try:
            _, data = mail.search(None, term)
            if data[0]:
                all_email_ids.update(data[0].split())
        except Exception as e:
            log.debug(f"Search term failed: {term}: {e}")

    log.info(f"Found {len(all_email_ids)} candidate emails")

    promotions = []
    processed = set()

    for email_id in all_email_ids:
        if email_id in processed:
            continue
        processed.add(email_id)

        try:
            _, msg_data = mail.fetch(email_id, "(RFC822)")
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)

            sender = decode_str(msg.get("From", ""))
            subject = decode_str(msg.get("Subject", ""))
            body = get_email_body(msg)

            # Check if it's a promo email
            if not is_promo_email(subject, body):
                continue

            # Identify programme
            prog_id = identify_programme(sender, subject)
            if not prog_id:
                log.debug(f"Unknown programme for: {sender} / {subject[:60]}")
                continue

            # Extract details
            promo = extract_promo_details(subject, body, prog_id)

            # Only include if we got at least a bonus % or end date
            if promo["bonus_pct"] or promo["end_date"]:
                promotions.append(promo)
                log.info(f"  Found promo: {promo['programme_name']} — {promo['discount_type']} (ends {promo['end_date']})")

        except Exception as e:
            log.debug(f"Error parsing email {email_id}: {e}")

    return promotions


def run_gmail_parser():
    """Parse Gmail accounts and write promotions to Google Sheets."""
    accounts = []

    account1 = os.environ.get("GMAIL_ACCOUNT_1")
    password1 = os.environ.get("GMAIL_PASSWORD_1")
    if account1 and password1:
        accounts.append((account1, password1))

    account2 = os.environ.get("GMAIL_ACCOUNT_2")
    password2 = os.environ.get("GMAIL_PASSWORD_2")
    if account2 and password2:
        accounts.append((account2, password2))

    if not accounts:
        log.error("No Gmail accounts configured. Add GMAIL_ACCOUNT_1/GMAIL_PASSWORD_1 to .env")
        return

    all_promotions = []

    for email_addr, password in accounts:
        log.info(f"Parsing Gmail: {email_addr}")
        try:
            mail = connect_gmail(email_addr, password)
            promos = fetch_promo_emails(mail)
            all_promotions.extend(promos)
            mail.logout()
            log.info(f"  {len(promos)} promotions found in {email_addr}")
        except imaplib.IMAP4.error as e:
            log.error(f"Gmail auth failed for {email_addr}: {e}")
            log.info("Check your App Password is correct and IMAP is enabled in Gmail settings")
        except Exception as e:
            log.error(f"Error parsing {email_addr}: {e}")

    if all_promotions:
        spreadsheet = get_spreadsheet()
        ws = ensure_sheet_structure(spreadsheet)
        added = write_promotions_to_sheet(ws, all_promotions)
        log.info(f"Gmail parse complete. {added} new records added to Sheets.")
    else:
        log.info("No new promotions found in Gmail.")


if __name__ == "__main__":
    run_gmail_parser()
