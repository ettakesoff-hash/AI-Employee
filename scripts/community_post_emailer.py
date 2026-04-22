"""
community_post_emailer.py — Weekly Monday Community Post Emailer

Scrapes AwardWallet's current buy-points promotions page, formats a
ready-to-paste community post, and emails it to hello@estelletramaine.com.

Runs automatically every Monday at 8am UTC via GitHub Actions.
Manual run: python scripts/community_post_emailer.py
"""

import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────

SOURCE_URL = "https://awardwallet.com/news/current-promotions-buy-points-miles/"

SEND_FROM = os.getenv("AUTOMATION_GMAIL", "estelletramaine.automation@gmail.com")
SEND_FROM_PASSWORD = os.getenv("AUTOMATION_GMAIL_PASSWORD", "").replace(" ", "")
SEND_TO = "hello@estelletramaine.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# Programmes worth highlighting — those usable for business class flights
# (Southwest and JetBlue excluded as they don't partner for int'l business class)
BUSINESS_CLASS_PROGRAMMES = {
    "alaska", "air canada", "aeroplan", "avianca", "lifemiles",
    "copa", "connectmiles", "united", "mileageplus", "virgin atlantic",
    "lufthansa", "miles & more", "etihad",
    "delta", "skymiles", "qatar", "air france", "flying blue", "klm",
    "finnair", "iberia", "emirates", "british airways", "ba avios",
    "singapore", "cathay", "ana ", "thai", "turkish", "tap air",
    "jetblue", "trueblue", "garuda",
}

# Programmes excluded regardless — not genuine promotions (e.g. always-on discounts)
EXCLUDED_PROGRAMMES = {
    "american",  # Always runs 40% off at 151K+ — not a real sale
    "aadvantage",
}


# ─────────────────────────────────────────────
# Parsing helpers
# ─────────────────────────────────────────────

def parse_date(text):
    """Parse a date string into a date object. Returns None if unparseable."""
    if not text:
        return None
    text = text.strip()
    for fmt in ["%B %d, %Y", "%b %d, %Y", "%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y"]:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def extract_cost_per_1000(text):
    """Extract cost per 1,000 points from strings like '1.47¢ per point'."""
    if not text:
        return None
    match = re.search(r"(\d+\.?\d*)[¢¢]", text)
    if match:
        cents = float(match.group(1))
        if cents < 0.1:
            cents *= 100
        return round(cents * 10, 2)
    return None


def is_business_class_programme(name):
    """Returns True if the programme is relevant for business class bookings."""
    name_lower = name.lower()
    return any(kw in name_lower for kw in BUSINESS_CLASS_PROGRAMMES)


# ─────────────────────────────────────────────
# Scraper
# ─────────────────────────────────────────────

def scrape_promotions():
    """
    Scrape the AwardWallet current promotions page.
    Returns a list of dicts: {name, bonus, cost_per_1000, end_date, end_date_raw}
    """
    print(f"Fetching {SOURCE_URL}")
    try:
        resp = requests.get(SOURCE_URL, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f"ERROR: Could not fetch page — {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    today = date.today()
    promotions = []
    seen_names = set()

    tables = soup.find_all("table")
    print(f"Found {len(tables)} table(s) on page")

    for table in tables:
        rows = table.find_all("tr")
        if len(rows) < 2:
            continue

        for row in rows[1:]:  # skip header row
            cells = row.find_all(["td", "th"])
            if not cells:
                continue

            texts = [c.get_text(strip=True) for c in cells]
            if not texts or not texts[0]:
                continue

            prog_name = texts[0]

            # Skip duplicates
            if prog_name.lower() in seen_names:
                continue

            # Find bonus % anywhere in the row
            bonus_str = ""
            for t in texts[1:]:
                m = re.search(r"(\d+)%\s*(?:bonus|discount|off|transfer)", t, re.IGNORECASE)
                if m:
                    bonus_str = t
                    break
            if not bonus_str:
                # Try any % mention
                for t in texts[1:]:
                    if "%" in t:
                        bonus_str = t
                        break

            # Find cost per point anywhere in the row
            cost_per_1000 = None
            for t in texts[1:]:
                c = extract_cost_per_1000(t)
                if c:
                    cost_per_1000 = c
                    break

            # Find end date anywhere in the row
            end_date = None
            end_date_raw = ""
            for t in texts[1:]:
                d = parse_date(t)
                if d:
                    end_date = d
                    end_date_raw = t
                    break

            # Skip rows with no bonus/discount info at all
            if not bonus_str and not cost_per_1000:
                continue

            # Skip already-expired promotions
            if end_date and end_date < today:
                continue

            # Skip permanently excluded programmes
            if any(kw in prog_name.lower() for kw in EXCLUDED_PROGRAMMES):
                print(f"  - {prog_name} (excluded)")
                continue

            seen_names.add(prog_name.lower())
            promotions.append({
                "name": prog_name,
                "bonus": bonus_str,
                "cost_per_1000": cost_per_1000,
                "end_date": end_date,
                "end_date_raw": end_date_raw,
                "is_business_class": is_business_class_programme(prog_name),
            })
            print(f"  + {prog_name} | {bonus_str} | cost/1k: {cost_per_1000} | ends: {end_date_raw}")

    print(f"Scraped {len(promotions)} active promotion(s)")
    return promotions


# ─────────────────────────────────────────────
# Post formatter
# ─────────────────────────────────────────────

def format_cost(cost_per_1000):
    """Format cost as '$14.70 per 1,000 pts'."""
    if cost_per_1000 is None:
        return None
    return f"${cost_per_1000:.2f} per 1,000 pts"


def format_end_date(end_date):
    """Format end date as 'Mon 27 Apr'."""
    if not end_date:
        return None
    return end_date.strftime("%a %d %b")


def format_community_post(promotions):
    """
    Build the ready-to-paste community post text.
    """
    today = date.today()
    expiry_window = today + timedelta(days=7)

    # Separate business class relevant vs others
    bc_promos = [p for p in promotions if p["is_business_class"]]
    other_promos = [p for p in promotions if not p["is_business_class"]]

    # Expiring within 7 days (business class programmes only)
    expiring_soon = [
        p for p in bc_promos
        if p["end_date"] and p["end_date"] <= expiry_window
    ]

    lines = []

    # Opening
    lines.append("Happy Monday everyone!")
    lines.append("")
    lines.append(
        "Here are the airline loyalty programmes currently running sales on buying points."
    )
    lines.append("")

    # Main promotions list
    if bc_promos:
        lines.append("CURRENT PROMOTIONS")
        lines.append("")
        for p in bc_promos:
            parts = [p["name"]]
            if p["bonus"]:
                parts.append(p["bonus"])
            if p["cost_per_1000"]:
                parts.append(format_cost(p["cost_per_1000"]))
            if p["end_date"]:
                parts.append(f"ends {format_end_date(p['end_date'])}")
            lines.append("• " + " — ".join(parts))
    else:
        # Fallback: show all programmes if none matched the business class filter
        lines.append("CURRENT PROMOTIONS")
        lines.append("")
        for p in promotions:
            parts = [p["name"]]
            if p["bonus"]:
                parts.append(p["bonus"])
            if p["cost_per_1000"]:
                parts.append(format_cost(p["cost_per_1000"]))
            if p["end_date"]:
                parts.append(f"ends {format_end_date(p['end_date'])}")
            lines.append("• " + " — ".join(parts))

    # Expiring soon section
    if expiring_soon:
        lines.append("")
        lines.append(
            "Please note, the following promotions are ending within the next 7 days:"
        )
        lines.append("")
        for p in expiring_soon:
            end_str = format_end_date(p["end_date"]) or "soon"
            lines.append(f"• {p['name']} — ends {end_str}")

    # Sign-off
    lines.append("")
    lines.append(
        "Please check your account for the exact pricing, as promotional offers "
        "and pricing can vary by account."
    )
    lines.append("")
    lines.append(
        "You can check the promotions at any time, by checking out the points promo dashboard:"
    )
    lines.append("https://points-dashboard.streamlit.app/")
    lines.append("")
    lines.append("If you need any help, feel free to reach out at any time.")

    return "\n".join(lines)


# ─────────────────────────────────────────────
# Email sender
# ─────────────────────────────────────────────

def send_email(subject, body_text):
    """Send a plain-text email via Gmail SMTP SSL."""
    msg = MIMEMultipart("alternative")
    msg["From"] = SEND_FROM
    msg["To"] = SEND_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(body_text, "plain"))

    print(f"Sending email to {SEND_TO} ...")
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SEND_FROM, SEND_FROM_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"ERROR sending email: {e}")
        raise


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    today = date.today()

    promotions = scrape_promotions()

    if not promotions:
        print("No promotions found — sending a heads-up email instead.")
        send_email(
            subject=f"Monday Community Post — {today.strftime('%d %B %Y')} [NO DATA]",
            body_text=(
                "Hi Estelle,\n\n"
                "The automated scraper ran this morning but found no active promotions "
                "on the AwardWallet page. You may want to check the page manually:\n\n"
                f"{SOURCE_URL}\n\n"
                "No community post has been generated this week."
            ),
        )
        return

    post_text = format_community_post(promotions)

    subject = f"Monday Community Post — {today.strftime('%d %B %Y')}"
    email_body = (
        f"Hi Estelle,\n\n"
        f"Here is your community post for this Monday. "
        f"Copy and paste everything below the line into your Go High Level community.\n\n"
        f"{'─' * 60}\n\n"
        f"{post_text}\n\n"
        f"{'─' * 60}\n\n"
        f"Found {len(promotions)} active promotion(s) this week.\n"
    )

    send_email(subject, email_body)
    print(f"\nPost preview:\n\n{post_text}\n")


if __name__ == "__main__":
    main()
