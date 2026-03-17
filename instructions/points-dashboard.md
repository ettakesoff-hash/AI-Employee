# Airline Points Promotions Dashboard

## What This Is
A real-time web dashboard for tracking when airline loyalty programmes put their points on sale. Clients access via a public Streamlit link. Data is stored in Google Sheets and updated daily by an automated scraper.

## Architecture
```
AwardWallet (12 programmes) ──┐
OneMilleAtATime (5 programmes) ├──► scraper → Google Sheets → Streamlit Dashboard → Clients
Gmail (2 accounts) ───────────┘
Manual entry (Google Sheets)
```

## Programme Coverage

### AwardWallet (scraped automatically)
| ID | Programme | Currency |
|----|-----------|----------|
| alaska | Alaska Airlines Mileage Plan | USD |
| aeroplan | Air Canada Aeroplan | CAD |
| lifemiles | Avianca LifeMiles | USD |
| connectmiles | Copa ConnectMiles | USD |
| mileageplus | United MileagePlus | USD |
| virgin_atlantic | Virgin Atlantic Flying Club | USD |
| miles_and_more | Lufthansa Miles & More | EUR |
| rapid_rewards | Southwest Rapid Rewards | USD |
| trueblue | JetBlue TrueBlue | USD |
| aadvantage | American AAdvantage | USD |
| etihad | Etihad Guest | USD |
| skymiles | Delta SkyMiles | USD |

### OneMilleAtATime (scraped automatically)
| ID | Programme | Currency |
|----|-----------|----------|
| qatar | Qatar Airways Privilege Club | USD |
| flying_blue | Air France-KLM Flying Blue | EUR |
| finnair | Finnair Plus | EUR |
| iberia | Iberia Plus | EUR |
| emirates | Emirates Skywards | USD |

### Email / Manual only
| ID | Programme | Notes |
|----|-----------|-------|
| ba_avios | British Airways Avios | Manual entry in Sheets |
| garuda | Garuda Indonesia GarudaMiles | Manual entry in Sheets |
| aer_lingus | Aer Lingus Avios | Manual entry in Sheets |

## Google Sheets Structure

**Sheet name:** Airline Points Promotions Dashboard

### Tab: `promotions`
| Column | Type | Example |
|--------|------|---------|
| programme_id | text | virgin_atlantic |
| programme_name | text | Virgin Atlantic Flying Club |
| start_date | date (YYYY-MM-DD) | 2026-03-01 |
| end_date | date (YYYY-MM-DD) | 2026-03-31 |
| bonus_pct | number | 70 |
| discount_type | text | 70% bonus |
| cost_per_1000pts_usd | number | 14.70 |
| native_currency | text | USD |
| cost_per_1000pts_native | number | 14.70 |
| source | text | awardwallet / onemileatatime / email / manual |
| notes | text | Max 300,000 points |
| added_date | date | 2026-03-17 |

### Tab: `base_prices`
**You update this manually when base prices change.**
| Column | Type | Example |
|--------|------|---------|
| programme_id | text | virgin_atlantic |
| programme_name | text | Virgin Atlantic Flying Club |
| base_cost_per_1000pts_usd | number | 30.50 |
| native_currency | text | USD |
| base_cost_per_1000pts_native | number | 30.50 |
| last_updated | date | 2026-03-17 |
| notes | text | Based on 100k-point tier |

### Tab: `programmes`
**Master list. Add new programmes here to include them in tracking.**
| Column | Type |
|--------|------|
| programme_id | text |
| programme_name | text |
| alliance | text |
| active | TRUE/FALSE |
| awardwallet_url | url |
| omaat_url | url |
| native_currency | text |

## Setup Steps

### Step 1: Google Cloud & Sheets API
1. Go to https://console.cloud.google.com
2. Create a new project: "Points Dashboard"
3. Enable APIs:
   - Google Sheets API
   - Google Drive API
4. Create credentials → Service Account
   - Name: "points-dashboard"
   - Role: Editor
5. Create key → JSON → download as `credentials/google-service-account.json`
6. Create a new Google Sheet, name it "Airline Points Promotions Dashboard"
7. Share the sheet with the service account email (from the JSON file)
8. Copy the Sheet ID from the URL (the long string between /d/ and /edit)
9. Add to `.env`: `GOOGLE_SHEET_ID=your_sheet_id_here`

### Step 2: Gmail IMAP (repeat for each Gmail account)
1. Go to your Google Account → Security → 2-Step Verification (must be ON)
2. Go to Security → App passwords
3. Create app password → Other → name it "Points Dashboard"
4. Copy the 16-character password
5. Add to `.env`:
   ```
   GMAIL_ACCOUNT_1=youremail@gmail.com
   GMAIL_PASSWORD_1=your-app-password
   GMAIL_ACCOUNT_2=secondemail@gmail.com
   GMAIL_PASSWORD_2=your-app-password
   ```

### Step 3: Run Initial Setup
```bash
cd /Users/estelleregis/AI-Employee
pip install -r requirements-dashboard.txt
python scripts/points_setup_sheets.py      # Creates tabs + imports historical data
python scripts/points_gmail_parser.py      # First Gmail import
```

### Step 4: Deploy to Streamlit Cloud
1. Push this repo to GitHub (or create a new public/private repo)
2. Go to https://share.streamlit.io
3. Connect GitHub → select repo → set main file: `scripts/points_dashboard.py`
4. Add secrets (Settings → Secrets) — paste contents of `.env`
5. Deploy → share the link with clients

### Step 5: Schedule Daily Updates
In Streamlit Cloud, the dashboard auto-refreshes on load. For the scraper, set up a GitHub Action:
- Create `.github/workflows/scrape_promotions.yml`
- Runs `points_scraper.py` daily at 8am UTC
- Credentials stored as GitHub Secrets

## Adding New Programmes
1. Find the airline's buy-points page on AwardWallet or OneMilleAtATime
2. Add a row to the `programmes` tab in Google Sheets
3. Add the programme config to `PROGRAMMES` dict in `points_scraper.py`
4. Run scraper to import history

## Data Source Notes
- **AwardWallet** updates within hours of a promotion going live. Most reliable source.
- **OneMilleAtATime** is slower to post deals but covers programmes AwardWallet doesn't.
- **Gmail** supplements with exact start dates (AwardWallet often only shows end dates).
- **Base prices**: Update manually in the `base_prices` tab whenever a programme changes its standard pricing. AwardWallet shows the no-promo rate on each programme page.

## Cost Per 1000 Points Conversion
All sources show "cents per point". Convert: `cents_per_point × 10 = cost_per_1000pts_in_USD`

Example: 1.47¢ per point → $14.70 per 1,000 points

## Troubleshooting
- **Scraper fails on AwardWallet**: Their HTML structure may have changed. Check the raw HTML and update the parser in `points_scraper.py`. Update this doc with the fix.
- **Gmail auth fails**: App password may have expired. Re-generate in Google Account settings.
- **Sheets quota error**: Google Sheets API has a 300 requests/minute limit. Add `time.sleep(1)` between batch writes if hitting this.
