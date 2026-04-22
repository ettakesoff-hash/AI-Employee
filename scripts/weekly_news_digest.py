#!/usr/bin/env python3
"""
weekly_news_digest.py — Weekly Points & Miles News Digest

Fetches articles from aviation and loyalty news blogs published in the last
7 days, filters out credit card content, uses Claude to select the 10 most
relevant stories and write a community-ready post, then emails it to
hello@estelletramaine.com every Wednesday.

Sources: Head for Points, One Mile at a Time, The Points Guy, Upgraded Points,
         AwardWallet Blog, View from the Wing, Loyalty Lobby.

Runs: Every Wednesday at 8am UTC via GitHub Actions.
Manual run: python scripts/weekly_news_digest.py
"""

import os
import re
import smtplib
import time
from datetime import date, datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import feedparser
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────

SEND_FROM = os.getenv("AUTOMATION_GMAIL", "estelletramaine.automation@gmail.com")
SEND_FROM_PASSWORD = os.getenv("AUTOMATION_GMAIL_PASSWORD", "").replace(" ", "")
SEND_TO = "hello@estelletramaine.com"

CUTOFF_DAYS = 7

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# All sources treated as RSS feeds. Standard blog RSS URLs.
RSS_SOURCES = [
    {"name": "Head for Points",    "url": "https://www.headforpoints.com/feed/"},
    {"name": "One Mile at a Time", "url": "https://onemileatatime.com/feed/"},
    {"name": "The Points Guy",     "url": "https://thepointsguy.com/feed/"},
    {"name": "Upgraded Points",    "url": "https://upgradedpoints.com/feed/"},
    {"name": "AwardWallet Blog",   "url": "https://awardwallet.com/blog/category/news/feed/"},
    {"name": "View from the Wing", "url": "https://viewfromthewing.com/feed/"},
    {"name": "Loyalty Lobby",      "url": "https://loyaltylobby.com/feed/"},
    {"name": "Point Hacks",        "url": "https://www.pointhacks.com.au/feed/"},
    {"name": "Australian Frequent Flyer", "url": "https://www.australianfrequentflyer.com.au/feed/"},
    {"name": "Prince of Travel",   "url": "https://princeoftravel.com/feed/"},
    {"name": "Frequent Miler",     "url": "https://frequentmiler.com/feed/"},
]

# Credit card exclusions — any ONE of these in the title triggers exclusion
CREDIT_CARD_TITLE_TRIGGERS = [
    "amex", "american express", "chase card", "barclays card",
    "capital one", "citibank", "citi card", "hsbc card",
    "lloyds card", "natwest card", "virgin money card",
]

# Credit card exclusions — 2+ of these in title+summary triggers exclusion
CREDIT_CARD_PHRASES = [
    "credit card", "credit cards", "card bonus", "signup bonus",
    "sign-up bonus", "welcome bonus", "annual fee", "best credit",
    "card review", "card comparison", "spending bonus", "card spend",
    "points from card", "debit card", "charge card",
]

# Hotel exclusions — any ONE match in title+summary excludes the article
HOTEL_PHRASES = [
    "world of hyatt", "park hyatt", "grand hyatt", "hyatt regency", "hyatt place",
    "hilton honors", "hilton hhonors", "hilton hotel", "marriott bonvoy",
    "ihg one rewards", "accor live", "radisson rewards", "global hotel alliance",
    "hotel loyalty", "hotel programme", "hotel program", "hotel reward",
    "hotel points", "hotel booking", "book a hotel", "hotel stay",
    "hotel night", "hotel credit", "nectar points", "tesco clubcard",
]

# Title patterns that indicate hotel award alerts or non-airline content
HOTEL_TITLE_PATTERNS = [
    r"^\[award alert\]",
    r"^book .{0,40} from \d+,\d+ points",
]

# How-to / educational content — matched against the article title
HOW_TO_PATTERNS = [
    r"\bhow to\b",
    r"^what is ",
    r"^what are ",
    r"^guide to ",
    r"^everything you need",
    r"^best ways? to ",
    r"^\d+ ways? to ",
    r"^\d+ best ",
    r"^tips for ",
    r"^beginners? guide",
    r" explained$",
    r"^understanding ",
    r"^your guide to",
    r"^the (ultimate|complete|full) guide",
    r"^award success",
    r"^trip report",
    r"^flight review",
    r"^review:",
    r" review$",
    r"^should you ",
    r"^why you should",
    r"^is it worth",
    r"^when (is|to) ",
    r"^best time to ",
    r"\bbased on offer history\b",
    # Weekly roundups and multi-story digests
    r"^bits:",
    r"the travel brief",
    r"\bnewsletter\b",
    r"^news roundup",
    r"^news in brief",
    r"^quick hits",
    r"^weekend roundup",
    r"^monday ",
    r"^friday ",
    r"\bweekly (roundup|round-up|digest|wrap|brief|recap)\b",
    r"\bthis week'?s?\b.*(news|update|recap|stories)",
]

# At least one of these must appear for an article to pass the relevance filter
RELEVANCE_KEYWORDS = [
    "airline", "flight", "points", "miles", "award", "loyalty",
    "programme", "program", "frequent flyer", "redemption", "reward",
    "alliance", "partnership", "codeshare", "route",
    "status", "business class", "first class", "upgrade",
    "avios", "flying blue", "aeroplan", "lifemiles", "mileage",
    "british airways", "virgin atlantic", "air france", "klm",
    "lufthansa", "singapore airlines", "cathay", "emirates",
    "etihad", "qatar", "united airlines", "delta", "ana ", "turkish",
    "oneworld", "star alliance", "skyteam",
    "peak", "off-peak", "devaluation", "valuation",
    "surcharge", "fuel surcharge", "transfer bonus",
]


# ─────────────────────────────────────────────
# Topic scoring — higher = more relevant to BCF audience
# ─────────────────────────────────────────────

TOPIC_SCORES = {
    # Highest priority — directly actionable for buying/using points
    "alliance": 4,
    "codeshare": 4,
    "devaluation": 4,
    "peak": 4,
    "off-peak": 4,
    "status match": 4,
    "status challenge": 4,
    "buy points": 4,
    "purchase points": 4,
    "buying points": 4,
    "fuel surcharge": 4,
    "award chart": 4,
    "programme change": 3,
    "program change": 3,
    "policy change": 3,
    "partnership": 3,
    "new route": 3,
    "route launch": 3,
    "earn points": 3,
    "earning miles": 3,
    "transfer bonus": 3,
    "redemption": 3,
    "award": 3,
    "loyalty": 2,
    "frequent flyer": 2,
    "business class": 2,
    "upgrade": 2,
}


# ─────────────────────────────────────────────
# Fetch
# ─────────────────────────────────────────────

def parse_entry_date(entry):
    """Extract a timezone-aware datetime from an RSS entry."""
    for attr in ("published_parsed", "updated_parsed"):
        val = getattr(entry, attr, None)
        if val:
            try:
                return datetime(*val[:6], tzinfo=timezone.utc)
            except Exception:
                continue
    return None


def clean_html(text):
    """Strip HTML tags and normalise whitespace."""
    if not text:
        return ""
    text = BeautifulSoup(text, "html.parser").get_text(" ", strip=True)
    return re.sub(r"\s+", " ", text).strip()


def fetch_rss_articles():
    """
    Fetch articles from all RSS sources published in the last CUTOFF_DAYS days.
    Returns a list of dicts: {source, title, link, summary, published}.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=CUTOFF_DAYS)
    all_articles = []

    for source in RSS_SOURCES:
        print(f"Fetching: {source['name']} ...")
        try:
            # Pre-fetch with browser headers — many sites block feedparser's default UA
            resp = requests.get(source["url"], headers=HEADERS, timeout=20)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
            count = 0
            for entry in feed.entries:
                pub_date = parse_entry_date(entry)
                if pub_date is None or pub_date < cutoff:
                    continue

                title = (entry.get("title") or "").strip()
                link = (entry.get("link") or "").strip()

                # Prefer full content over summary when available
                summary = ""
                if hasattr(entry, "content") and entry.content:
                    summary = entry.content[0].get("value", "")
                if not summary:
                    summary = entry.get("summary") or entry.get("description") or ""

                summary = clean_html(summary)[:300]  # Cap at 300 chars

                all_articles.append({
                    "source": source["name"],
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "published": pub_date.strftime("%d %b %Y"),
                })
                count += 1

            print(f"  {count} articles in last {CUTOFF_DAYS} days")

        except Exception as e:
            print(f"  ERROR fetching {source['name']}: {e}")

        time.sleep(1)  # Be polite between requests

    print(f"\nTotal fetched: {len(all_articles)} articles across {len(RSS_SOURCES)} sources")
    return all_articles


# ─────────────────────────────────────────────
# Filter
# ─────────────────────────────────────────────

def is_credit_card_article(title, summary):
    """Returns True if the article is primarily about credit card products."""
    title_lower = title.lower()
    combined = (title_lower + " " + summary.lower())
    # Hard exclude: card brand names in the title
    if any(trigger in title_lower for trigger in CREDIT_CARD_TITLE_TRIGGERS):
        return True
    # Soft exclude: 2+ credit card phrases anywhere in title+summary
    matches = sum(1 for phrase in CREDIT_CARD_PHRASES if phrase in combined)
    return matches >= 2


def is_hotel_article(title, summary):
    """Returns True if the article is primarily about hotel loyalty or bookings."""
    title_lower = title.lower()
    combined = (title_lower + " " + summary.lower())
    if any(phrase in combined for phrase in HOTEL_PHRASES):
        return True
    if any(re.search(p, title_lower) for p in HOTEL_TITLE_PATTERNS):
        return True
    return False


def is_how_to_article(title):
    """Returns True if the article is a how-to guide, roundup, or educational piece."""
    title_lower = title.lower()
    if any(re.search(pattern, title_lower) for pattern in HOW_TO_PATTERNS):
        return True
    # Multi-story roundup: title contains 3+ commas (e.g. "Story A, Story B, Story C")
    if title.count(",") >= 2:
        return True
    return False


def is_relevant(title, summary):
    """Returns True if the article is broadly relevant to aviation/loyalty points."""
    combined = (title + " " + summary).lower()
    return any(kw in combined for kw in RELEVANCE_KEYWORDS)


def filter_articles(articles):
    """Remove off-topic articles and keep only airline/points news."""
    filtered = []
    excluded_cc = 0
    excluded_hotel = 0
    excluded_howto = 0
    excluded_irrelevant = 0

    for a in articles:
        if is_credit_card_article(a["title"], a["summary"]):
            excluded_cc += 1
            continue
        if is_hotel_article(a["title"], a["summary"]):
            excluded_hotel += 1
            continue
        if is_how_to_article(a["title"]):
            excluded_howto += 1
            continue
        if not is_relevant(a["title"], a["summary"]):
            excluded_irrelevant += 1
            continue
        filtered.append(a)

    print(
        f"After filtering: {len(filtered)} relevant articles "
        f"({excluded_cc} credit card, {excluded_hotel} hotel, "
        f"{excluded_howto} how-to, {excluded_irrelevant} irrelevant excluded)"
    )
    return filtered


# ─────────────────────────────────────────────
# Select and format digest (no AI required)
# ─────────────────────────────────────────────

def score_article(article):
    """Score an article by topic relevance to the BCF audience."""
    combined = (article["title"] + " " + article["summary"]).lower()
    return sum(v for k, v in TOPIC_SCORES.items() if k in combined)


def deduplicate(articles):
    """
    Remove near-duplicate articles (same story covered by multiple blogs).
    Keeps the highest-scored version of each story.
    """
    seen_words = []
    unique = []
    for a in articles:
        # Build a fingerprint from the first 5 significant words of the title
        words = re.findall(r"\b[a-z]{4,}\b", a["title"].lower())[:5]
        fingerprint = set(words)
        # If 3+ words overlap with a seen title, treat as duplicate
        is_dupe = any(len(fingerprint & seen) >= 3 for seen in seen_words)
        if not is_dupe:
            seen_words.append(fingerprint)
            unique.append(a)
    return unique


def select_top_articles(articles, n=30):
    """Score, deduplicate, and return the top n articles."""
    for a in articles:
        a["score"] = score_article(a)
    # Sort by score descending, then by most recent
    articles.sort(key=lambda a: (a["score"], a["published"]), reverse=True)
    articles = deduplicate(articles)
    return articles[:n]


def format_digest(articles, today):
    """Format the selected articles into a ready-to-paste community post."""
    week_label = today.strftime("%d %B %Y")
    lines = []

    # Post title
    lines.append(f"This Week in Points and Miles — {week_label}")
    lines.append("")

    # Opening
    lines.append("Happy Wednesday everyone!")
    lines.append("")
    lines.append(
        "Here is your weekly roundup of the biggest changes in points, miles and aviation. "
        "Use it to stay on top of what is moving across the programmes this week."
    )

    for a in articles:
        lines.append("")
        lines.append("---")
        lines.append("")
        # Subheading — article title in title case
        lines.append(a["title"].strip())
        lines.append("")
        # Summary from RSS feed
        if a["summary"]:
            lines.append(a["summary"].strip())
            lines.append("")
        lines.append(f"Read more: {a['link']}")
        lines.append(f"Source: {a['source']}")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(
        "If you have questions about how any of this affects your points strategy, drop them below."
    )

    return "\n".join(lines)


# ─────────────────────────────────────────────
# Email
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
        print("Email sent.")
    except Exception as e:
        print(f"ERROR sending email: {e}")
        raise


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    today = date.today()
    week_label = today.strftime("%d %B %Y")

    # Step 1: Fetch
    articles = fetch_rss_articles()

    if not articles:
        send_email(
            subject=f"Wednesday Digest — {week_label} [NO ARTICLES FETCHED]",
            body_text=(
                "Hi Estelle,\n\n"
                "The weekly digest ran but could not fetch any articles from the sources.\n"
                "This may be a temporary network issue. The script will try again next Wednesday.\n\n"
                "If this happens repeatedly, check the script logs in GitHub Actions."
            ),
        )
        return

    # Step 2: Filter
    filtered = filter_articles(articles)

    if not filtered:
        send_email(
            subject=f"Wednesday Digest — {week_label} [NOTHING RELEVANT THIS WEEK]",
            body_text=(
                "Hi Estelle,\n\n"
                f"The digest fetched {len(articles)} articles this week but found nothing "
                "relevant after filtering out credit card content and off-topic pieces.\n\n"
                "This is unusual — worth checking the sources manually this week."
            ),
        )
        return

    # Step 3: Select top 10 and format
    top = select_top_articles(filtered, n=30)
    print(f"Top {len(top)} articles selected.")
    for a in top:
        print(f"  [{a['score']}] {a['title'][:70]}")

    digest = format_digest(top, today)

    # Step 4: Email
    email_subject = f"Wednesday Points & Miles Digest — {week_label}"
    email_body = (
        "Hi Estelle,\n\n"
        "Here are this week's top 30 stories. Pick the ones you want to use "
        "and copy them into your community post.\n\n"
        f"{'─' * 60}\n\n"
        f"{digest}\n\n"
        f"{'─' * 60}\n\n"
        f"Sources: {len(RSS_SOURCES)} blogs | "
        f"Articles fetched: {len(articles)} | "
        f"Relevant after filtering: {len(filtered)} | "
        f"Selected for digest: {len(top)}\n"
    )

    send_email(email_subject, email_body)
    print("\nDone.")


if __name__ == "__main__":
    main()
