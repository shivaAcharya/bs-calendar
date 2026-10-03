"""Unit tests for RFC 5545 compliance, line folding, escaping, and icalendar parser validation."""

import datetime
from pathlib import Path
import icalendar
import pytest

from bs_calendar.converter import from_bs
from bs_calendar.feed import (
    build_calendar_feed,
    create_day_event,
    escape_ics_text,
    fold_line,
    write_calendar_file,
)


class TestFormattingAndFolding:
    """Test RFC 5545 text escaping and 75-octet line folding."""

    def test_escape_ics_text(self) -> None:
        raw = "Hello, world; with \\ backslash and \n newlines."
        escaped = escape_ics_text(raw)
        assert r"\," in escaped
        assert r"\;" in escaped
        assert r"\\" in escaped
        assert r"\n" in escaped
        assert "\n" not in escaped
        assert "\r" not in escaped

    def test_fold_line_short(self) -> None:
        short = "SUMMARY:Short line"
        assert fold_line(short) == short

    def test_fold_line_long_ascii(self) -> None:
        long_line = "DESCRIPTION:" + "A" * 150
        folded = fold_line(long_line)
        lines = folded.split("\r\n")
        assert len(lines) > 1
        for i, l in enumerate(lines):
            octets = len(l.encode("utf-8"))
            assert octets <= 75, f"Line {i} exceeds 75 octets: {octets}"
            if i > 0:
                assert l.startswith(" "), f"Continuation line {i} must start with space"

    def test_fold_line_multibyte_devanagari_not_split(self) -> None:
        # Devanagari string with multi-byte UTF-8 sequences (3 bytes each)
        nepali_text = "DESCRIPTION:" + "नेपाली पात्रो र वि.सं. मिति क्यालेन्डर " * 5
        folded = fold_line(nepali_text)
        lines = folded.split("\r\n")

        for i, l in enumerate(lines):
            # Check octet limit
            assert len(l.encode("utf-8")) <= 75
            # Ensure valid UTF-8 and no broken characters
            decoded = l.encode("utf-8").decode("utf-8")
            assert decoded == l
            if i > 0:
                assert l.startswith(" ")


class TestICSCorrectnessWithParser:
    """Verify generated feeds against the authoritative python `icalendar` parser."""

    @pytest.fixture
    def sample_dates(self) -> list:
        # A small 5-day span around month boundary: 2083 Ashwin 30, 31, and Kartik 1, 2, 3
        # Ashwin in 2083 has 31 days
        return [
            from_bs(2083, 6, 30),
            from_bs(2083, 6, 31),
            from_bs(2083, 7, 1),
            from_bs(2083, 7, 2),
            from_bs(2083, 7, 3),
        ]

    def test_en_feed_parsed_by_icalendar(self, sample_dates: list) -> None:
        ics_text = build_calendar_feed(sample_dates, lang="en", dtstamp="20261001T000000Z")

        # Verify CRLF integrity
        assert ics_text.endswith("\r\n")
        # Every newline should be part of \r\n
        assert "\r\n" in ics_text
        assert len(ics_text.split("\r\n")) - 1 == ics_text.count("\n")

        # Parse with icalendar
        cal = icalendar.Calendar.from_ical(ics_text.encode("utf-8"))

        # Verify Calendar Header Properties
        assert str(cal.get("VERSION")) == "2.0"
        assert str(cal.get("CALSCALE")) == "GREGORIAN"
        assert "Nepali Date (BS)" in str(cal.get("X-WR-CALNAME"))
        assert str(cal.get("X-WR-TIMEZONE")) == "Asia/Kathmandu"
        assert str(cal.get("X-PUBLISHED-TTL")) == "P1D"

        # Verify Events
        events = cal.walk("VEVENT")
        assert len(events) == len(sample_dates)

        for ev, bs_d in zip(events, sample_dates):
            # Deterministic UID check
            expected_uid = f"{bs_d.gregorian_date.isoformat()}-en@bs-calendar"
            assert str(ev.get("UID")) == expected_uid

            # TRANSP:TRANSPARENT check
            assert str(ev.get("TRANSP")) == "TRANSPARENT"

            # All-day event checks
            dtstart = ev.get("DTSTART").dt
            dtend = ev.get("DTEND").dt
            assert isinstance(dtstart, datetime.date)
            assert isinstance(dtend, datetime.date)
            assert dtstart == bs_d.gregorian_date
            # Exclusive end: next day
            assert dtend - dtstart == datetime.timedelta(days=1)

            # Summary check
            summary = str(ev.get("SUMMARY"))
            if bs_d.day == 1:
                assert summary == f"{bs_d.month_name_en} 1, {bs_d.year}"
            else:
                assert summary == f"{bs_d.month_name_en} {bs_d.day}"

            # Description check
            desc = str(ev.get("DESCRIPTION"))
            assert f"Bikram Sambat: {bs_d.month_name_en}" in desc
            assert bs_d.gregorian_date.isoformat() in desc

    def test_ne_feed_parsed_by_icalendar(self, sample_dates: list) -> None:
        ics_text = build_calendar_feed(sample_dates, lang="ne", dtstamp="20261001T000000Z")
        cal = icalendar.Calendar.from_ical(ics_text.encode("utf-8"))

        # Calendar Header
        assert "नेपाली" in str(cal.get("X-WR-CALNAME"))
        assert str(cal.get("X-WR-TIMEZONE")) == "Asia/Kathmandu"

        events = cal.walk("VEVENT")
        assert len(events) == len(sample_dates)

        for ev, bs_d in zip(events, sample_dates):
            expected_uid = f"{bs_d.gregorian_date.isoformat()}-ne@bs-calendar"
            assert str(ev.get("UID")) == expected_uid
            assert str(ev.get("TRANSP")) == "TRANSPARENT"

            summary = str(ev.get("SUMMARY"))
            assert bs_d.month_name_ne in summary

    def test_write_calendar_file(self, tmp_path: Path, sample_dates: list) -> None:
        target = tmp_path / "dist" / "bs-calendar-en.ics"
        written = write_calendar_file(target, sample_dates, lang="en")
        assert written.is_file()

        raw_bytes = target.read_bytes()
        # Verify valid UTF-8
        decoded = raw_bytes.decode("utf-8")
        assert decoded.endswith("\r\n")

        # Verify parsed
        cal = icalendar.Calendar.from_ical(raw_bytes)
        assert len(cal.walk("VEVENT")) == len(sample_dates)
