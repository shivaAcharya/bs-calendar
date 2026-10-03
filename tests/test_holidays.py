"""Unit tests for optional holidays extension point."""

import datetime
import json
from pathlib import Path
import icalendar

from bs_calendar.converter import from_bs
from bs_calendar.feed import build_calendar_feed
from bs_calendar.holidays import Holiday, load_holidays, parse_holiday_entry


def test_missing_holidays_file_returns_empty_list() -> None:
    non_existent = Path("data/non_existent_holidays.json")
    holidays = load_holidays(non_existent)
    assert holidays == []


def test_parse_holiday_entry_with_both_dates() -> None:
    entry = {
        "bs_date": "2083-01-01",
        "gregorian_date": "2026-04-14",
        "name_en": "Nepali New Year",
        "name_ne": "नयाँ वर्ष",
        "description": "Celebration of Bikram Sambat New Year",
    }
    h = parse_holiday_entry(entry)
    assert h is not None
    assert h.bs_date_str == "2083-01-01"
    assert h.gregorian_date == datetime.date(2026, 4, 14)
    assert h.name_en == "Nepali New Year"
    assert h.name_ne == "नयाँ वर्ष"
    assert h.description == "Celebration of Bikram Sambat New Year"
    assert h.summary("en") == "Nepali New Year"
    assert h.summary("ne") == "नयाँ वर्ष"


def test_parse_holiday_entry_derive_gregorian_from_bs() -> None:
    entry = {
        "bs_date": "2083-01-01",
        "name_en": "Nepali New Year",
        "name_ne": "नयाँ वर्ष",
    }
    h = parse_holiday_entry(entry)
    assert h is not None
    assert h.gregorian_date == datetime.date(2026, 4, 14)


def test_parse_holiday_entry_derive_bs_from_gregorian() -> None:
    entry = {
        "gregorian_date": "2026-04-14",
        "name_en": "Nepali New Year",
        "name_ne": "नयाँ वर्ष",
    }
    h = parse_holiday_entry(entry)
    assert h is not None
    assert h.bs_date_str == "2083-01-01"


def test_holiday_event_injected_into_feed(tmp_path: Path) -> None:
    sample_date = from_bs(2083, 1, 1)
    holiday = Holiday(
        gregorian_date=sample_date.gregorian_date,
        bs_date_str="2083-01-01",
        name_en="Nepali New Year",
        name_ne="नयाँ वर्ष",
        description="Public holiday in Nepal",
    )

    ics_content = build_calendar_feed([sample_date], lang="en", holidays=[holiday])
    cal = icalendar.Calendar.from_ical(ics_content.encode("utf-8"))
    events = cal.walk("VEVENT")

    # Should have 2 events: 1 date event + 1 holiday event
    assert len(events) == 2

    holiday_events = [e for e in events if "holiday-" in str(e.get("UID"))]
    assert len(holiday_events) == 1
    h_ev = holiday_events[0]
    assert str(h_ev.get("SUMMARY")) == "Nepali New Year"
    assert str(h_ev.get("TRANSP")) == "TRANSPARENT"
    assert "Public holiday in Nepal" in str(h_ev.get("DESCRIPTION"))


def test_load_holidays_from_file(tmp_path: Path) -> None:
    holidays_file = tmp_path / "holidays.json"
    data = [
        {
            "bs_date": "2083-01-01",
            "gregorian_date": "2026-04-14",
            "name_en": "Nepali New Year",
            "name_ne": "नयाँ वर्ष",
        }
    ]
    holidays_file.write_text(json.dumps(data), encoding="utf-8")

    loaded = load_holidays(holidays_file)
    assert len(loaded) == 1
    assert loaded[0].name_en == "Nepali New Year"
