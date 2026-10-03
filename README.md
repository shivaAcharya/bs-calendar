# Bikram Sambat (BS, Nepali) Calendar Feed Generator

A Python project that generates subscribable `.ics` (iCalendar) feeds displaying the Bikram Sambat (BS, नेपाली पात्रो) date for every day. Users can subscribe to the feed in **Google Calendar**, **Apple Calendar**, or **Outlook** via "Add from URL" to view Nepali dates on Web, Android, and iOS.

---

## Features

- **Daily All-Day Events:** Displays the BS date every day (e.g. `Ashwin 17` or `आश्विन १७`).
- **Month Start Context:** The first day of each BS month includes the month and year (e.g. `Ashwin 1, 2083` or `आश्विन १, २०८३`).
- **Full Date Descriptions:** Each event contains:
  - Bikram Sambat date in English
  - Bikram Sambat date in Nepali (Devanagari) with the day of the week
  - Full Gregorian (AD) date
- **Dual Feeds:**
  - `bs-calendar-en.ics`: English month names (`Baisakh`, `Jestha`, `Ashadh`, `Shrawan`, `Bhadra`, `Ashwin`, `Kartik`, `Mangsir`, `Poush`, `Magh`, `Falgun`, `Chaitra`) and Western Arabic numerals.
  - `bs-calendar-ne.ics`: Devanagari month names and numerals (`वैशाख`, `जेष्ठ`, `असार`, `श्रावण`, `भाद्र`, `आश्विन`, `कार्तिक`, `मंसिर`, `पौष`, `माघ`, `फाल्गुन`, `चैत्र`, `०..९`).
- **RFC 5545 & Google Calendar Compliance:**
  - Strict CRLF (`\r\n`) line endings.
  - Maximum 75-octet line folding that respects UTF-8 multi-byte character boundaries.
  - Proper escaping of commas, semicolons, and backslashes in text fields.
  - `TRANSP:TRANSPARENT` ensures events do not mark users as busy.
  - Deterministic UIDs (e.g., `2026-10-03-en@bs-calendar`) so periodic feed updates refresh existing events rather than duplicating them.
  - Refresh headers (`X-PUBLISHED-TTL:P1D` and `REFRESH-INTERVAL;VALUE=DURATION:P1D`).
- **Automated Deployment:** GitHub Actions automatically tests, regenerates, and publishes feeds to GitHub Pages on a monthly schedule and on push.

---

## Subscribing to the Calendar Feed

### Step 1: Copy the Feed URL

Once published to GitHub Pages, your feed URLs will look like:

- **English Feed:**
  ```text
  https://shivaacharya.github.io/bs-calendar/bs-calendar-en.ics
  ```
- **Nepali Feed (देवनागरी):**
  ```text
  https://shivaacharya.github.io/bs-calendar/bs-calendar-ne.ics
  ```

### Step 2: Add to Google Calendar (Web)

1. Open [Google Calendar](https://calendar.google.com) on your desktop browser.
2. In the left sidebar, scroll down to **"Other calendars"** and click the **`+`** (plus) icon.
3. Select **"From URL"**.
4. Paste your copied `.ics` feed URL.
5. Click **"Add calendar"**.

> **One-Click Subscription Alternative:**
> Visiting the GitHub Pages landing page (`index.html`) gives you a 1-click **"Add to Google Calendar"** button using the `webcal://` protocol.

### Step 3: Enable Mobile Sync (Android & iOS)

> [!IMPORTANT]
> **Mobile Sync Note:**
> Google Calendar does **not** automatically sync newly subscribed web feeds to mobile apps by default. To make it appear on your phone:
> 1. Open the **Google Calendar app** on your Android device or iPhone.
> 2. Open the side menu (`☰`) and tap **Settings**.
> 3. Under your Google account, tap **Show more** / find the newly subscribed calendar (`Nepali Date (BS)`).
> 4. Tap the calendar and turn the **Sync** toggle **ON**.

---

## Data Source, Accuracy & Range Limits

### Nature of Bikram Sambat
Unlike the Gregorian calendar, Bikram Sambat month lengths vary between **29 and 32 days** from year to year. Month lengths depend on astronomical solar ingress (*Sankranti*) into zodiac constellations calculated by the **Nepal Panchanga Nirnayak Samiti** (the official calendar determination committee of Nepal). Therefore, BS dates cannot be derived through mathematical formulas; they require authoritative astronomical lookup tables.

### Underlying Library and Lookup Table
- **Library:** [`nepali-datetime`](https://pypi.org/project/nepali-datetime/) (MIT License).
- **Lookup Source:** Backed by `calendar_bs.csv`, compiled from official Government of Nepal / Panchanga Nirnayak Samiti published almanacs.

### Supported Date Range
| Metric | Range |
| :--- | :--- |
| **Bikram Sambat Years** | **1975 BS to 2100 BS** (inclusive, 126 years) |
| **Gregorian (AD) Dates** | **1918-04-13 to 2044-04-12** |

### Verified Anchor Dates
The conversion engine is validated in automated unit tests against official anchor dates:
- **1 Baisakh 2082 BS** = **14 April 2025 AD** (Nepali New Year 2082)
- **1 Baisakh 2081 BS** = **13 April 2024 AD** (Nepali New Year 2081)
- **1 Baisakh 2080 BS** = **14 April 2023 AD** (Nepali New Year 2080)
- **1 Baisakh 2083 BS** = **14 April 2026 AD** (Nepali New Year 2083)
- **1 Baisakh 2078 BS** = **14 April 2021 AD** (Nepali New Year 2078)
- **Leap Year Handling:** 29 February 2024 AD = 17 Falgun 2080 BS

### Out-of-Range Guardrails
If any date outside **1975–2100 BS** is requested, the converter immediately raises a descriptive `DateOutOfRangeError` rather than guessing or producing invalid dates.

---

## Installation & CLI Usage

### Prerequisites
- Python 3.11+
- Git

### Setup
```bash
# Clone the repository
git clone https://github.com/shivaAcharya/bs-calendar.git
cd bs-calendar

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies (including pytest and icalendar)
pip install -e ".[dev]"
```

### Running the Generator CLI
To regenerate feeds locally:
```bash
python -m bs_calendar generate --years 3 --out dist/
```

#### CLI Options
```text
options:
  --years INT        Number of BS years to generate from the start year (default: 3).
  --start-year INT   Starting BS year (default: current BS year).
  --out PATH         Output folder for feeds and index.html (default: dist/).
  --holidays PATH    Optional holidays JSON file (default: data/holidays.json).
  -q, --quiet        Suppress console output.
```

Generated outputs in `dist/`:
- `dist/bs-calendar-en.ics` (English feed)
- `dist/bs-calendar-ne.ics` (Nepali Devanagari feed)
- `dist/index.html` (Landing page with 1-click subscription and copy links)

---

## Optional Extension Point: Holidays

The generator supports an optional `data/holidays.json` file. If present, it injects holiday events alongside the daily date events.

Format of `data/holidays.json`:
```json
[
  {
    "bs_date": "2083-01-01",
    "gregorian_date": "2026-04-14",
    "name_en": "Nepali New Year",
    "name_ne": "नयाँ वर्ष",
    "description": "Public holiday in Nepal"
  }
]
```
*(By default, this file is intentionally not included in the repository to prevent inventing unverified holiday data).*

---

## Running Tests

The test suite thoroughly verifies:
- Anchor dates and round-trip AD &harr; BS conversions
- Month transitions and year rollovers
- Gregorian leap years
- Out-of-range bounds checking
- Event title formatting (Day 1 vs subsequent days)
- RFC 5545 escaping and UTF-8 75-octet line folding
- Strict parsing and property verification using `icalendar`
- Optional holiday parsing and injection

Run all tests:
```bash
pytest -v
```

---

## GitHub Actions & GitHub Pages Deployment

The included workflow (`.github/workflows/deploy.yml`):
1. **Triggers:**
   - On push to `main` / `master`
   - On schedule (1st of every month at midnight UTC) via `cron: "0 0 1 * *"` to maintain a fresh 3-year rolling window
   - Manual run via `workflow_dispatch`
2. **Steps:**
   - Installs dependencies and runs `pytest`
   - Runs `python -m bs_calendar generate --years 3 --out dist/`
   - Deploys `dist/` directly to **GitHub Pages**

### Enabling GitHub Pages
1. Go to your repository on GitHub &rarr; **Settings** &rarr; **Pages**.
2. Under **Build and deployment** &rarr; **Source**, select **GitHub Actions**.
3. Push to `main` or trigger the workflow manually to publish.
