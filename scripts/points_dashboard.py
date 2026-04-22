"""
points_dashboard.py — Airline Points Promotions Dashboard

Streamlit web app. Shows current promotions, historical price charts,
and promotion frequency stats. Clients access via a public link.

Run locally: streamlit run scripts/points_dashboard.py
Deploy:      Streamlit Cloud → connect GitHub repo → main file: scripts/points_dashboard.py
"""

import os
import json
from datetime import date, datetime, timedelta
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
import requests
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Airline Points Promotions",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Styling
# ─────────────────────────────────────────────

st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0.25rem;
    }
    .sub-header {
        color: #666;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .promo-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
    }
    .promo-card h3 {
        margin: 0 0 0.5rem 0;
        font-size: 1.1rem;
    }
    .promo-card .deal-badge {
        background: rgba(255,255,255,0.25);
        border-radius: 99px;
        padding: 0.2rem 0.7rem;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    .promo-card .cost {
        font-size: 1.4rem;
        font-weight: 700;
    }
    .promo-card .meta {
        font-size: 0.8rem;
        opacity: 0.8;
        margin-top: 0.25rem;
    }
    .stat-box {
        background: #f8f9ff;
        border: 1px solid #e0e4ff;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .stat-box .number {
        font-size: 1.6rem;
        font-weight: 700;
        color: #667eea;
    }
    .stat-box .label {
        font-size: 0.8rem;
        color: #888;
        margin-top: 0.25rem;
    }
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1a1a2e;
        margin: 2rem 0 1rem 0;
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.5rem;
    }
    .days-left {
        font-size: 0.75rem;
        background: rgba(255,100,100,0.2);
        border-radius: 99px;
        padding: 0.1rem 0.5rem;
        display: inline-block;
    }
    .days-left.urgent { background: rgba(255,50,50,0.3); font-weight: 700; }
    .last-seen { color: #888; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Data Loading
# ─────────────────────────────────────────────

ALLIANCE_COLOURS = {
    "Star Alliance": "#1a1a2e",
    "Oneworld": "#c0392b",
    "SkyTeam": "#2980b9",
    "None": "#7f8c8d",
}

CURRENCY_SYMBOLS = {
    "USD": "$", "GBP": "£", "EUR": "€", "AUD": "A$",
    "CAD": "C$", "SGD": "S$", "NZD": "NZ$", "AED": "AED ",
    "JPY": "¥", "CHF": "CHF ", "HKD": "HK$", "THB": "฿",
    "INR": "₹", "ZAR": "R",
}


def connect_sheets():
    """Connect to Google Sheets using service account or Streamlit secrets."""
    scopes = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    # Try Streamlit secrets first (for cloud deployment), fall back to local JSON
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    except Exception:
        creds_path = Path(__file__).parent.parent / "credentials" / "google-service-account.json"
        creds = Credentials.from_service_account_file(str(creds_path), scopes=scopes)

    return gspread.authorize(creds)


def get_sheet_id():
    try:
        return st.secrets["GOOGLE_SHEET_ID"]
    except Exception:
        return os.environ.get("GOOGLE_SHEET_ID", "")


def _parse_promo_df(records):
    """Parse raw sheet records into a typed DataFrame."""
    df = pd.DataFrame(records)
    if df.empty:
        return df
    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce")
    df["added_date"] = pd.to_datetime(df["added_date"], errors="coerce")
    df["bonus_pct"] = pd.to_numeric(df["bonus_pct"], errors="coerce")
    df["cost_per_1000pts_usd"] = pd.to_numeric(df["cost_per_1000pts_usd"], errors="coerce")
    df["cost_per_1000pts_native"] = pd.to_numeric(df["cost_per_1000pts_native"], errors="coerce")
    return df


@st.cache_data(ttl=3600)
def load_promotions():
    """Load full promotions history from Google Sheets."""
    try:
        client = connect_sheets()
        spreadsheet = client.open_by_key(get_sheet_id())
        records = spreadsheet.worksheet("promotions").get_all_records()
        return _parse_promo_df(records)
    except Exception as e:
        st.error(f"Could not load data from Google Sheets: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_current_promotions():
    """Load today's active promotions from the current_promos tab (cleared daily by scraper)."""
    try:
        client = connect_sheets()
        spreadsheet = client.open_by_key(get_sheet_id())
        records = spreadsheet.worksheet("current_promos").get_all_records()
        return _parse_promo_df(records)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_base_prices():
    """Load base prices from Google Sheets."""
    try:
        client = connect_sheets()
        spreadsheet = client.open_by_key(get_sheet_id())
        ws = spreadsheet.worksheet("base_prices")
        records = ws.get_all_records()
        df = pd.DataFrame(records)
        df["base_cost_per_1000pts_usd"] = pd.to_numeric(df["base_cost_per_1000pts_usd"], errors="coerce")
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=7200)
def get_fx_rates(base_currency="USD"):
    """Fetch exchange rates. Free API, no key needed."""
    try:
        resp = requests.get(
            f"https://open.er-api.com/v6/latest/{base_currency}",
            timeout=10
        )
        data = resp.json()
        if data.get("result") == "success":
            return data["rates"]
    except Exception:
        pass
    # Fallback rates if API fails
    return {
        "USD": 1.0, "GBP": 0.79, "EUR": 0.92, "AUD": 1.54,
        "CAD": 1.36, "SGD": 1.34, "NZD": 1.65, "AED": 3.67,
        "JPY": 149.5, "CHF": 0.88, "HKD": 7.82, "THB": 35.1,
        "INR": 83.1, "ZAR": 18.6,
    }


def convert_price(usd_amount, target_currency, rates):
    """Convert USD amount to target currency."""
    if pd.isna(usd_amount) or usd_amount == 0:
        return None
    rate = rates.get(target_currency, 1.0)
    return round(usd_amount * rate, 2)


def get_display_price(row, selected_currency, rates):
    """Get price for display — uses USD if available, otherwise converts from native currency."""
    usd = row.get("cost_per_1000pts_usd")
    if pd.notna(usd) and usd:
        return convert_price(float(usd), selected_currency, rates)
    # Fall back: convert native currency → USD → selected currency
    native = row.get("cost_per_1000pts_native")
    native_currency = row.get("native_currency", "USD")
    if pd.notna(native) and native and native_currency and native_currency in rates:
        usd_equiv = float(native) / rates[native_currency]  # native → USD
        return convert_price(usd_equiv, selected_currency, rates)
    return None


def format_price(amount, currency):
    """Format price with currency symbol."""
    if amount is None or pd.isna(amount):
        return "—"
    symbol = CURRENCY_SYMBOLS.get(currency, f"{currency} ")
    return f"{symbol}{amount:,.2f}"


def format_promotion(row):
    """Format promotion as '160% bonus' or '50% off' from bonus_pct + discount_type."""
    discount_type = str(row.get("discount_type", "") or "")
    bonus_pct = row.get("bonus_pct")
    if pd.notna(bonus_pct) and bonus_pct:
        pct = int(bonus_pct)
        if "discount" in discount_type.lower() or "off" in discount_type.lower():
            return f"{pct}% off"
        return f"{pct}% bonus"
    return discount_type if discount_type else "Promotion"


# ─────────────────────────────────────────────
# Promo Analysis Helpers
# ─────────────────────────────────────────────

def get_promo_stats(df, programme_id):
    """Get promotion frequency stats for a programme."""
    prog_df = df[df["programme_id"] == programme_id].dropna(subset=["end_date"]).copy()
    prog_df = prog_df.sort_values("end_date")

    today = pd.Timestamp(date.today())
    stats = {}

    # Last promotion ended
    past = prog_df[prog_df["end_date"] < today]
    if not past.empty:
        last_end = past["end_date"].iloc[-1]
        days_ago = (today - last_end).days
        if days_ago < 7:
            stats["last_promo"] = f"{days_ago} day{'s' if days_ago != 1 else ''} ago"
        elif days_ago < 30:
            stats["last_promo"] = f"{days_ago // 7} week{'s' if days_ago // 7 != 1 else ''} ago"
        else:
            months = days_ago // 30
            stats["last_promo"] = f"{months} month{'s' if months != 1 else ''} ago"
    else:
        stats["last_promo"] = "No history"

    # Gap between promos (weeks)
    gaps_days = []
    if len(prog_df) >= 2:
        dates = prog_df["end_date"].tolist()
        for i in range(1, len(dates)):
            gap = (dates[i] - dates[i - 1]).days
            if 0 < gap < 400:
                gaps_days.append(gap)

    if gaps_days:
        avg_gap = sum(gaps_days) / len(gaps_days)
        avg_gap_weeks = avg_gap / 7
        stats["avg_gap_weeks"] = f"{avg_gap_weeks:.1f} weeks"
        stats["avg_gap_days"] = avg_gap
        if avg_gap < 14:
            stats["frequency"] = "Every 1–2 weeks"
        elif avg_gap < 35:
            stats["frequency"] = "~Monthly"
        elif avg_gap < 70:
            stats["frequency"] = "Every 1–2 months"
        elif avg_gap < 120:
            stats["frequency"] = "Every 2–3 months"
        else:
            freq_per_year = round(365 / avg_gap, 1)
            stats["frequency"] = f"~{freq_per_year:.0f}× per year"
    else:
        stats["avg_gap_weeks"] = "—"
        stats["avg_gap_days"] = None
        stats["frequency"] = f"{len(prog_df)} recorded"

    # Average promo duration (days)
    durations = []
    for _, row in prog_df.iterrows():
        if pd.notna(row.get("start_date")) and pd.notna(row.get("end_date")):
            d = (row["end_date"] - row["start_date"]).days
            if 1 <= d <= 90:
                durations.append(d)
    if durations:
        avg_dur = sum(durations) / len(durations)
        stats["avg_duration"] = f"{avg_dur:.0f} days"
    else:
        stats["avg_duration"] = "—"

    # Best ever bonus
    if not prog_df["bonus_pct"].isna().all():
        best = prog_df["bonus_pct"].max()
        stats["best_bonus"] = f"{int(best)}% bonus"
        stats["best_bonus_pct"] = int(best)
    else:
        stats["best_bonus"] = "—"
        stats["best_bonus_pct"] = None

    # Mode (most common) bonus
    if not prog_df["bonus_pct"].isna().all():
        mode_val = prog_df["bonus_pct"].dropna().mode()
        if not mode_val.empty:
            stats["mode_bonus"] = f"{int(mode_val.iloc[0])}% bonus"
            stats["mode_bonus_pct"] = int(mode_val.iloc[0])
        else:
            stats["mode_bonus"] = "—"
            stats["mode_bonus_pct"] = None
    else:
        stats["mode_bonus"] = "—"
        stats["mode_bonus_pct"] = None

    # Median bonus
    if not prog_df["bonus_pct"].isna().all():
        typical = prog_df["bonus_pct"].median()
        stats["typical_bonus"] = f"{int(typical)}% bonus"
        stats["typical_bonus_pct"] = int(typical)
    else:
        stats["typical_bonus"] = "—"
        stats["typical_bonus_pct"] = None

    stats["total_promos"] = len(prog_df)
    return stats


# ─────────────────────────────────────────────
# Main Dashboard
# ─────────────────────────────────────────────

def main():
    today = date.today()
    today_ts = pd.Timestamp(today)

    # Load data
    df = load_promotions()           # Full history — used for chart + stats
    current = load_current_promotions()  # Today's active promos — used for cards
    base_df = load_base_prices()
    fx_rates = get_fx_rates()

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### ✈️ Airline Points Promotions")
        st.markdown("*Track buy-points deals across loyalty programmes*")
        st.divider()

        # Currency selector
        all_currencies = sorted(CURRENCY_SYMBOLS.keys())
        selected_currency = st.selectbox(
            "Display currency",
            options=all_currencies,
            index=all_currencies.index("USD"),
            help="All prices converted from USD at today's exchange rate"
        )
        currency_symbol = CURRENCY_SYMBOLS.get(selected_currency, selected_currency + " ")

        st.divider()

        # Data freshness
        st.markdown("**Data last updated**")
        if not df.empty and "added_date" in df.columns:
            latest = df["added_date"].max()
            if pd.notna(latest):
                st.caption(latest.strftime("%d %b %Y"))
        else:
            st.caption("Unknown")

        if st.button("🔄 Refresh data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        st.divider()
        st.caption(f"Updated daily · {len(df):,} promotions tracked")
        st.caption(f"Exchange rate: 1 USD = {fx_rates.get(selected_currency, 1):.4f} {selected_currency}")

    # ── Header ───────────────────────────────────────────────────────────────
    st.markdown('<div class="main-header">✈️ Airline Points Promotions</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="sub-header">Real-time tracking of buy-points deals · '
        f'Updated daily · Prices in {selected_currency}</div>',
        unsafe_allow_html=True
    )

    if df.empty:
        st.warning("No data loaded. Run the scraper first: `python scripts/points_scraper.py`")
        st.info("Then run the historical import: `python scripts/points_import_history.py`")
        return

    # ── Current Promotions ───────────────────────────────────────────────────
    st.markdown('<div class="section-title">🔥 Currently On Sale</div>', unsafe_allow_html=True)

    OPEN_ENDED = pd.Timestamp("2099-12-31")
    # current is loaded directly from current_promos tab (cleared + rewritten daily)
    if not current.empty:
        current = current.sort_values("bonus_pct", ascending=False, na_position="last")

    if current.empty:
        st.info("No active promotions found right now. Check back soon!")
    else:

        # Summary stats row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="stat-box">
                <div class="number">{len(current)}</div>
                <div class="label">Programmes on sale</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            best_bonus = current["bonus_pct"].max()
            st.markdown(f"""
            <div class="stat-box">
                <div class="number">{int(best_bonus) if pd.notna(best_bonus) else '—'}%</div>
                <div class="label">Best bonus available</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            soonest = current["end_date"].min()
            days_left = (soonest - today_ts).days if pd.notna(soonest) else None
            st.markdown(f"""
            <div class="stat-box">
                <div class="number">{days_left if days_left is not None else '—'}</div>
                <div class="label">Days until first expiry</div>
            </div>""", unsafe_allow_html=True)
        with col4:
            best_cost = current["cost_per_1000pts_usd"].min()
            converted = convert_price(best_cost, selected_currency, fx_rates)
            st.markdown(f"""
            <div class="stat-box">
                <div class="number">{format_price(converted, selected_currency)}</div>
                <div class="label">Cheapest per 1,000 pts</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("")

        # Promotion cards — 3 per row
        cols_per_row = 3
        rows = [current.iloc[i:i+cols_per_row] for i in range(0, len(current), cols_per_row)]

        for row_data in rows:
            cols = st.columns(cols_per_row)
            for col, (_, promo) in zip(cols, row_data.iterrows()):
                days_left = (promo["end_date"] - today_ts).days if pd.notna(promo["end_date"]) else None
                cost_display = get_display_price(promo, selected_currency, fx_rates)
                promo_label = format_promotion(promo)

                urgency = ""
                if days_left is not None:
                    if days_left <= 3:
                        urgency = "⚠️ "
                    elif days_left <= 7:
                        urgency = "🔴 "

                with col:
                    is_open_ended = pd.notna(promo["end_date"]) and promo["end_date"].year == 2099
                    end_str = "No end date published" if is_open_ended else (promo["end_date"].strftime("%d %b %Y") if pd.notna(promo["end_date"]) else "—")
                    days_str = "" if is_open_ended else (f"{days_left} days left" if days_left is not None else "")
                    days_line = f"<br>{days_str}" if days_str else ""
                    cost_str = format_price(cost_display, selected_currency) if cost_display else "—"

                    st.markdown(f"""
                    <div class="promo-card">
                        <div class="deal-badge">{promo_label}</div>
                        <h3>{urgency}{promo['programme_name']}</h3>
                        <div class="cost">{cost_str} <small style="font-size:0.7rem;opacity:0.8">per 1,000 pts</small></div>
                        <div class="meta">
                            Ends: {end_str}{days_line}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # Table view toggle
        with st.expander("📋 View as table"):
            table_data = current[[
                "programme_name", "start_date", "end_date",
                "bonus_pct", "discount_type",
                "cost_per_1000pts_usd", "cost_per_1000pts_native", "native_currency"
            ]].copy()

            table_data["Promotion"] = current.apply(format_promotion, axis=1)
            table_data[f"Cost / 1,000 pts ({selected_currency})"] = table_data.apply(
                lambda r: get_display_price(r, selected_currency, fx_rates), axis=1
            )
            table_data["Promo Start Date"] = table_data["start_date"].dt.strftime("%d %b %Y").fillna("—")
            table_data["Promo End Date"] = table_data["end_date"].apply(
                lambda x: "Open-ended" if pd.notna(x) and x.year == 2099 else (x.strftime("%d %b %Y") if pd.notna(x) else "—")
            )

            display_cols = {
                "programme_name": "Programme",
                "Promo Start Date": "Promo Start Date",
                "Promo End Date": "Promo End Date",
                "Promotion": "Promotion",
                f"Cost / 1,000 pts ({selected_currency})": f"Cost / 1,000 pts ({selected_currency})",
            }
            out = pd.DataFrame({v: table_data[k] for k, v in display_cols.items()})
            st.dataframe(out, use_container_width=True, hide_index=True)

    # ── Historical Chart ─────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📈 Price History</div>', unsafe_allow_html=True)

    all_programmes = sorted(df["programme_name"].dropna().unique().tolist())
    selected_progs = st.multiselect(
        "Select programmes to compare",
        options=all_programmes,
        default=all_programmes[:3] if len(all_programmes) >= 3 else all_programmes,
        help="Select one or more programmes to see their promotion history"
    )

    if selected_progs:
        chart_df = df[df["programme_name"].isin(selected_progs)].copy()
        chart_df = chart_df[chart_df["end_date"].notna()]

        # Convert cost to selected currency (uses native currency fallback for CAD/EUR programmes)
        chart_df["cost_display"] = chart_df.apply(
            lambda r: get_display_price(r, selected_currency, fx_rates), axis=1
        )

        # Add base prices to chart
        base_lines = {}
        if not base_df.empty:
            for _, bp_row in base_df.iterrows():
                prog_name = bp_row.get("programme_name", "")
                if prog_name in selected_progs:
                    base_usd = bp_row.get("base_cost_per_1000pts_usd")
                    if pd.notna(base_usd) and base_usd:
                        base_lines[prog_name] = convert_price(float(base_usd), selected_currency, fx_rates)

        fig = go.Figure()
        colours = px.colors.qualitative.Set2

        for i, prog_name in enumerate(selected_progs):
            prog_data = chart_df[chart_df["programme_name"] == prog_name].sort_values("end_date")

            if prog_data.empty:
                continue

            colour = colours[i % len(colours)]

            # Draw promotion periods as horizontal bars + scatter points
            has_cost_data = prog_data["cost_display"].notna().any()

            if has_cost_data:
                # Plot cost per 1000 pts over time
                prog_with_cost = prog_data[prog_data["cost_display"].notna()]

                # Create step-chart effect using start/end dates
                x_vals, y_vals = [], []
                for _, row in prog_with_cost.iterrows():
                    start = row["start_date"] if pd.notna(row["start_date"]) else row["end_date"] - pd.Timedelta(days=30)
                    end = row["end_date"]
                    cost = row["cost_display"]
                    x_vals.extend([start, end, None])
                    y_vals.extend([cost, cost, None])

                fig.add_trace(go.Scatter(
                    x=x_vals, y=y_vals,
                    mode="lines",
                    name=prog_name,
                    line=dict(color=colour, width=3),
                    hovertemplate=(
                        f"<b>{prog_name}</b><br>"
                        f"Cost: {currency_symbol}%{{y:.2f}} per 1,000 pts<br>"
                        "<extra></extra>"
                    ),
                ))

                # Scatter dots at end dates
                fig.add_trace(go.Scatter(
                    x=prog_with_cost["end_date"],
                    y=prog_with_cost["cost_display"],
                    mode="markers",
                    showlegend=False,
                    marker=dict(color=colour, size=8, symbol="circle"),
                    text=prog_with_cost["discount_type"],
                    hovertemplate=(
                        f"<b>{prog_name}</b><br>"
                        "Deal: %{text}<br>"
                        f"Cost: {currency_symbol}%{{y:.2f}} per 1,000 pts<br>"
                        "Ends: %{x|%d %b %Y}<br>"
                        "<extra></extra>"
                    ),
                ))
            else:
                # No cost data — show as timeline bars by bonus %
                prog_with_bonus = prog_data[prog_data["bonus_pct"].notna()]
                if not prog_with_bonus.empty:
                    fig.add_trace(go.Scatter(
                        x=prog_with_bonus["end_date"],
                        y=prog_with_bonus["bonus_pct"],
                        mode="markers+lines",
                        name=prog_name,
                        line=dict(color=colour, width=2, dash="dot"),
                        marker=dict(size=8),
                        text=prog_with_bonus["discount_type"],
                        hovertemplate=(
                            f"<b>{prog_name}</b><br>"
                            "Deal: %{text}<br>"
                            "Bonus: %{y:.0f}%<br>"
                            "Ends: %{x|%d %b %Y}<br>"
                            "<extra></extra>"
                        ),
                    ))

            # Base price line
            if prog_name in base_lines:
                fig.add_hline(
                    y=base_lines[prog_name],
                    line_dash="dash",
                    line_color=colour,
                    opacity=0.4,
                    annotation_text=f"{prog_name} base",
                    annotation_position="right",
                )

        # Today line — using add_shape to avoid plotly version incompatibility with add_vline
        fig.add_shape(
            type="line",
            x0=today.isoformat(), x1=today.isoformat(),
            y0=0, y1=1,
            xref="x", yref="paper",
            line=dict(dash="dash", color="red", width=1),
            opacity=0.5,
        )
        fig.add_annotation(
            x=today.isoformat(), y=1.05,
            xref="x", yref="paper",
            text="Today",
            showarrow=False,
            font=dict(color="red", size=11),
        )

        has_cost = chart_df["cost_display"].notna().any()
        y_label = f"Cost per 1,000 pts ({selected_currency})" if has_cost else "Bonus %"

        chart_start_24m = (today - timedelta(days=730)).isoformat()
        fig.update_layout(
            title="",
            xaxis_title="Date",
            yaxis_title=y_label,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=450,
            margin=dict(l=40, r=40, t=20, b=40),
            xaxis=dict(showgrid=True, gridcolor="#f0f0f0", range=[chart_start_24m, today.isoformat()]),
            yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        )

        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "💡 Lower = better deal. Dashed horizontal lines show standard (non-promotion) price. "
            "The red vertical line is today."
        )

    # ── Programme Stats ──────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📊 Programme Intelligence</div>', unsafe_allow_html=True)
    st.markdown("Select a programme to see its promotion patterns and whether the current deal is good value.")

    prog_options = sorted(df["programme_id"].dropna().unique().tolist())
    prog_display = {
        pid: df[df["programme_id"] == pid]["programme_name"].iloc[0]
        for pid in prog_options
        if not df[df["programme_id"] == pid].empty
    }

    selected_stat_prog = st.selectbox(
        "Programme",
        options=prog_options,
        format_func=lambda x: prog_display.get(x, x),
    )

    if selected_stat_prog:
        stats = get_promo_stats(df, selected_stat_prog)
        prog_name = prog_display.get(selected_stat_prog, selected_stat_prog)

        # Check if currently on sale
        is_current = selected_stat_prog in current["programme_id"].values if not current.empty else False
        if is_current:
            st.success(f"✅ **{prog_name}** is currently on sale!")
        else:
            st.info(f"ℹ️ **{prog_name}** is not currently on sale.")

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1:
            st.markdown(f"""
            <div class="stat-box">
                <div class="number">{stats['last_promo']}</div>
                <div class="label">Last promo ended</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="stat-box">
                <div class="number">{stats['avg_gap_weeks']}</div>
                <div class="label">Avg weeks between promos</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="stat-box">
                <div class="number">{stats['avg_duration']}</div>
                <div class="label">Avg promo duration</div>
            </div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="stat-box">
                <div class="number">{stats['best_bonus']}</div>
                <div class="label">Best ever bonus</div>
            </div>""", unsafe_allow_html=True)
        with c5:
            st.markdown(f"""
            <div class="stat-box">
                <div class="number">{stats['mode_bonus']}</div>
                <div class="label">Most common bonus</div>
            </div>""", unsafe_allow_html=True)
        with c6:
            st.markdown(f"""
            <div class="stat-box">
                <div class="number">{stats['typical_bonus']}</div>
                <div class="label">Median bonus</div>
            </div>""", unsafe_allow_html=True)

        # Current deal assessment vs history
        if is_current and not current.empty:
            current_row = current[current["programme_id"] == selected_stat_prog].iloc[0]
            current_bonus = current_row.get("bonus_pct")
            best_pct = stats.get("best_bonus_pct")
            mode_pct = stats.get("mode_bonus_pct")
            if pd.notna(current_bonus) and current_bonus:
                current_bonus = int(current_bonus)
                if best_pct and current_bonus >= best_pct * 0.95:
                    st.success(f"🏆 **Exceptional deal** — this is at or near the best bonus ever seen for {prog_name}. Buy now.")
                elif mode_pct and current_bonus > mode_pct:
                    st.success(f"👍 **Above average** — {current_bonus}% is better than the most common bonus ({mode_pct}%) for {prog_name}.")
                elif mode_pct and current_bonus == mode_pct:
                    st.info(f"📊 **Typical deal** — {current_bonus}% is the most common bonus level for {prog_name}. Solid but not exceptional.")
                elif mode_pct and current_bonus < mode_pct:
                    st.warning(f"⚠️ **Below average** — {current_bonus}% is lower than the usual {mode_pct}% bonus for {prog_name}. Consider waiting.")

        # History table for this programme
        prog_history = df[df["programme_id"] == selected_stat_prog].sort_values("end_date", ascending=False).copy()
        prog_history["Promotion"] = prog_history.apply(format_promotion, axis=1)
        prog_history[f"Cost/1,000 pts ({selected_currency})"] = prog_history.apply(
            lambda r: get_display_price(r, selected_currency, fx_rates), axis=1
        )
        prog_history["Promo Start Date"] = prog_history["start_date"].dt.strftime("%d %b %Y").fillna("—")
        prog_history["Promo End Date"] = prog_history["end_date"].apply(
            lambda x: "Open-ended" if pd.notna(x) and x.year == 2099 else (x.strftime("%d %b %Y") if pd.notna(x) else "—")
        )

        hist_out = prog_history[["Promo Start Date", "Promo End Date", "Promotion", f"Cost/1,000 pts ({selected_currency})"]].copy()

        with st.expander(f"Full history — {prog_name} ({stats['total_promos']} promotions recorded)"):
            st.dataframe(hist_out, use_container_width=True, hide_index=True)

    # ── Footer ───────────────────────────────────────────────────────────────
    st.divider()
    st.caption(
        "Prices are estimates based on published rates and may vary by account tier, region, and purchase volume. "
        f"Exchange rates updated every 2 hours. Last page load: {datetime.now().strftime('%d %b %Y %H:%M')} UTC."
    )


if __name__ == "__main__":
    main()
