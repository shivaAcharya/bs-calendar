"""Command line interface for bs-calendar feed generator."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from bs_calendar.constants import MAX_BS_YEAR, MIN_BS_YEAR
from bs_calendar.converter import (
    DateOutOfRangeError,
    get_current_bs_year,
    iter_bs_dates,
)
from bs_calendar.feed import write_calendar_file
from bs_calendar.holidays import load_holidays


def generate_index_html(
    start_year: int,
    end_year: int,
    total_days: int,
) -> str:
    """Generate a modern HTML landing page for GitHub Pages with subscription links."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Bikram Sambat (BS) Calendar Feeds</title>
  <style>
    :root {{
      --primary: #c2410c;
      --primary-hover: #9a3412;
      --bg: #0f172a;
      --card-bg: #1e293b;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --border: #334155;
      --accent: #38bdf8;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
      padding: 2rem 1rem;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
    }}
    .container {{
      max-width: 800px;
      width: 100%;
    }}
    header {{
      text-align: center;
      margin-bottom: 2.5rem;
    }}
    h1 {{
      font-size: 2.25rem;
      font-weight: 800;
      color: #fb923c;
      margin-bottom: 0.5rem;
    }}
    .subtitle {{
      color: var(--text-muted);
      font-size: 1.1rem;
    }}
    .stats-badge {{
      display: inline-block;
      margin-top: 0.75rem;
      padding: 0.35rem 0.85rem;
      border-radius: 9999px;
      background: rgba(251, 146, 60, 0.15);
      color: #fdba74;
      font-size: 0.875rem;
      font-weight: 600;
      border: 1px solid rgba(251, 146, 60, 0.3);
    }}
    .cards-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2.5rem;
    }}
    .card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 1rem;
      padding: 1.75rem;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
      transition: transform 0.2s, border-color 0.2s;
    }}
    .card:hover {{
      transform: translateY(-2px);
      border-color: #fb923c;
    }}
    .card-title {{
      font-size: 1.35rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}
    .card-desc {{
      color: var(--text-muted);
      font-size: 0.95rem;
      margin-bottom: 1.25rem;
    }}
    .btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      width: 100%;
      padding: 0.75rem 1rem;
      border-radius: 0.5rem;
      font-size: 0.95rem;
      font-weight: 600;
      text-decoration: none;
      cursor: pointer;
      border: none;
      transition: all 0.2s;
      margin-bottom: 0.6rem;
    }}
    .btn-primary {{
      background: var(--primary);
      color: white;
    }}
    .btn-primary:hover {{
      background: var(--primary-hover);
    }}
    .btn-outline {{
      background: transparent;
      border: 1px solid var(--border);
      color: var(--text);
    }}
    .btn-outline:hover {{
      background: rgba(255, 255, 255, 0.05);
      border-color: var(--accent);
    }}
    .url-box {{
      font-size: 0.8rem;
      padding: 0.5rem;
      background: #0f172a;
      border-radius: 0.375rem;
      color: #94a3b8;
      word-break: break-all;
      margin-top: 0.5rem;
      user-select: all;
    }}
    .instructions {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 1rem;
      padding: 2rem;
      margin-bottom: 2.5rem;
    }}
    .instructions h2 {{
      font-size: 1.4rem;
      margin-bottom: 1rem;
      color: #38bdf8;
    }}
    .instructions ol {{
      margin-left: 1.5rem;
      margin-bottom: 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
    }}
    .instructions li strong {{
      color: #f1f5f9;
    }}
    .note-box {{
      background: rgba(56, 189, 248, 0.1);
      border-left: 4px solid var(--accent);
      padding: 1rem;
      border-radius: 0.375rem;
      font-size: 0.9rem;
      color: #bae6fd;
    }}
    footer {{
      text-align: center;
      color: var(--text-muted);
      font-size: 0.85rem;
      padding-top: 1rem;
      border-top: 1px solid var(--border);
    }}
    footer a {{ color: #fb923c; text-decoration: none; }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>नेपाली पात्रो (Bikram Sambat Calendar)</h1>
      <p class="subtitle">Subscribable .ics calendar feeds for Google Calendar, Apple Calendar, and Outlook</p>
      <div class="stats-badge">Coverage: BS {start_year} – {end_year} ({total_days:,} days)</div>
    </header>

    <div class="cards-grid">
      <!-- English Feed Card -->
      <div class="card">
        <h3 class="card-title">English Feed (bs-calendar-en.ics)</h3>
        <p class="card-desc">English month names (e.g. "Ashwin 17", "Kartik 1, 2083") with Western Arabic numerals.</p>
        <button class="btn btn-primary" onclick="subscribeGoogle('bs-calendar-en.ics')">Add to Google Calendar</button>
        <button class="btn btn-outline" onclick="copyFeedUrl('bs-calendar-en.ics')">Copy Feed URL</button>
        <div class="url-box" id="url-en">...</div>
      </div>

      <!-- Nepali Feed Card -->
      <div class="card">
        <h3 class="card-title">नेपाली पात्रो (bs-calendar-ne.ics)</h3>
        <p class="card-desc">देवनागरी महिना र अङ्कहरू (जस्तै: "आश्विन १७", "कार्तिक १, २०८३")।</p>
        <button class="btn btn-primary" onclick="subscribeGoogle('bs-calendar-ne.ics')">Google Calendar मा थप्नुहोस्</button>
        <button class="btn btn-outline" onclick="copyFeedUrl('bs-calendar-ne.ics')">Feed URL प्रतिलिपि गर्नुहोस्</button>
        <div class="url-box" id="url-ne">...</div>
      </div>
    </div>

    <div class="instructions">
      <h2>How to Add to Google Calendar</h2>
      <ol>
        <li>Open <strong>Google Calendar</strong> on your desktop browser (calendar.google.com).</li>
        <li>In the left sidebar, click the <strong>+</strong> next to <strong>"Other calendars"</strong>.</li>
        <li>Select <strong>"From URL"</strong> from the menu.</li>
        <li>Paste the copied Feed URL from above.</li>
        <li>Click <strong>"Add calendar"</strong>. Done!</li>
      </ol>
      <div class="note-box">
        <strong>Mobile Sync Note (Android & iOS):</strong> Newly added web feeds do not automatically appear in the mobile Google Calendar app by default. To display them on your phone: open the Google Calendar app &rarr; go to <strong>Settings</strong> &rarr; find your account and tap the new calendar &rarr; toggle <strong>Sync</strong> to ON.
      </div>
    </div>

    <footer>
      <p>Generated by Bikram Sambat Calendar Feed Generator &bull; Authoritative BS astronomical data (1975–2100 BS)</p>
    </footer>
  </div>

  <script>
    function getFullUrl(filename) {{
      const loc = window.location.href.split('#')[0].split('?')[0];
      const base = loc.endsWith('/') ? loc : loc.substring(0, loc.lastIndexOf('/') + 1);
      return base + filename;
    }}
    document.getElementById('url-en').textContent = getFullUrl('bs-calendar-en.ics');
    document.getElementById('url-ne').textContent = getFullUrl('bs-calendar-ne.ics');

    function copyFeedUrl(filename) {{
      const url = getFullUrl(filename);
      navigator.clipboard.writeText(url).then(() => {{
        alert('Copied feed URL to clipboard:\\n' + url);
      }}).catch(() => {{
        prompt('Copy feed URL:', url);
      }});
    }}

    function subscribeGoogle(filename) {{
      const feedUrl = getFullUrl(filename);
      const cleanUrl = feedUrl.replace(/^https?:\\/\\//, '');
      const gcalUrl = 'https://calendar.google.com/calendar/render?cid=' + encodeURIComponent('webcal://' + cleanUrl);
      window.open(gcalUrl, '_blank');
    }}
  </script>
</body>
</html>
"""


def build_parser() -> argparse.ArgumentParser:
    """Build command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="python -m bs_calendar",
        description="Generate subscribable Bikram Sambat (BS) calendar feeds (.ics).",
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # generate command
    gen_parser = subparsers.add_parser("generate", help="Generate ICS calendar feeds")
    _add_generate_args(gen_parser)

    # Allow running flags directly on root parser as fallback
    _add_generate_args(parser)

    return parser


def _add_generate_args(parser: argparse.ArgumentParser) -> None:
    """Add arguments common to generation."""
    parser.add_argument(
        "--years",
        type=int,
        default=None,
        help="Number of BS years to generate, starting from start-year.",
    )
    parser.add_argument(
        "--start-year",
        type=int,
        default=None,
        help=(
            f"Starting Bikram Sambat year (default: current BS year, "
            f"range: {MIN_BS_YEAR}..{MAX_BS_YEAR})."
        ),
    )
    parser.add_argument(
        "--end-year",
        type=int,
        default=None,
        help=(
            f"Ending Bikram Sambat year (default: {MAX_BS_YEAR} BS or start-year + years - 1, "
            f"range: {MIN_BS_YEAR}..{MAX_BS_YEAR})."
        ),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("dist"),
        help="Output directory where .ics files and index.html are saved (default: dist/).",
    )
    parser.add_argument(
        "--holidays",
        type=Path,
        default=Path("data/holidays.json"),
        help="Path to optional holidays.json file (default: data/holidays.json).",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress console progress output.",
    )


def run_generate(
    years: int | None = None,
    start_year: int | None = None,
    end_year: int | None = None,
    out_dir: Path = Path("dist"),
    holidays_file: Path | None = None,
    quiet: bool = False,
) -> int:
    """Execute calendar generation."""
    current_bs_year = get_current_bs_year()
    if start_year is None:
        start_year = current_bs_year

    if not (MIN_BS_YEAR <= start_year <= MAX_BS_YEAR):
        sys.stderr.write(
            f"Error: Requested start year {start_year} is out of supported "
            f"bounds ({MIN_BS_YEAR}..{MAX_BS_YEAR} BS).\n"
        )
        return 1

    if end_year is not None:
        if end_year < start_year:
            sys.stderr.write(
                f"Error: --end-year ({end_year}) cannot be earlier than --start-year ({start_year}).\n"
            )
            return 1
        years = end_year - start_year + 1
    elif years is not None:
        if years < 1:
            sys.stderr.write(f"Error: --years must be at least 1, got {years}.\n")
            return 1
        end_year = start_year + years - 1
    else:
        # Default: extend through maximum supported year (2100 BS)
        end_year = MAX_BS_YEAR
        years = end_year - start_year + 1

    if not (MIN_BS_YEAR <= end_year <= MAX_BS_YEAR) or years < 1:
        sys.stderr.write(
            f"Error: Requested year range ({start_year}..{end_year} BS) is out of supported "
            f"bounds ({MIN_BS_YEAR}..{MAX_BS_YEAR} BS).\n"
        )
        return 1

    if not quiet:
        print(f"Generating Bikram Sambat feeds for {years} year(s): BS {start_year} -> {end_year}")

    try:
        dates_list = list(iter_bs_dates(start_year=start_year, num_years=years))
    except DateOutOfRangeError as err:
        sys.stderr.write(f"Date conversion error: {err}\n")
        return 1

    # Load optional holidays if present
    holidays = load_holidays(holidays_file)
    if not quiet:
        if holidays:
            print(f"Loaded {len(holidays)} optional holiday(s) from {holidays_file}")
        else:
            print(f"No holidays file found or empty ({holidays_file}); continuing without holidays.")

    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. English feed
    en_file = out_dir / "bs-calendar-en.ics"
    write_calendar_file(en_file, dates=dates_list, lang="en", holidays=holidays)
    if not quiet:
        print(f"Created: {en_file} ({len(dates_list)} date events)")

    # 2. Nepali feed
    ne_file = out_dir / "bs-calendar-ne.ics"
    write_calendar_file(ne_file, dates=dates_list, lang="ne", holidays=holidays)
    if not quiet:
        print(f"Created: {ne_file} ({len(dates_list)} date events)")

    # 3. HTML Landing page
    html_file = out_dir / "index.html"
    html_content = generate_index_html(
        start_year=start_year,
        end_year=end_year,
        total_days=len(dates_list),
    )
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    if not quiet:
        print(f"Created: {html_file}")

    if not quiet:
        print("Successfully generated all feeds!")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)

    return run_generate(
        years=args.years,
        start_year=args.start_year,
        end_year=args.end_year,
        out_dir=args.out,
        holidays_file=args.holidays,
        quiet=args.quiet,
    )


if __name__ == "__main__":
    sys.exit(main())
