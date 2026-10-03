"""RFC 5545 iCalendar feed builder with Google Calendar compatibility."""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Iterable, Sequence

from bs_calendar.constants import (
    CALNAME_EN,
    CALNAME_NE,
    CALSCALE,
    PRODID,
    PUBLISHED_TTL,
    REFRESH_INTERVAL,
    TIMEZONE_STR,
    VERSION,
)
from bs_calendar.converter import BSDate
from bs_calendar.holidays import Holiday


def escape_ics_text(text: str) -> str:
    """Escape text for RFC 5545 compliance (backslash, semicolon, comma, newline)."""
    text = text.replace("\\", "\\\\")
    text = text.replace(";", "\\;")
    text = text.replace(",", "\\,")
    text = text.replace("\r\n", "\\n").replace("\r", "\\n").replace("\n", "\\n")
    return text


def fold_line(line: str, max_octets: int = 75) -> str:
    """Fold a single content line so no physical line exceeds `max_octets` UTF-8 bytes.

    According to RFC 5545 §3.1, lines are folded by inserting CRLF followed by
    a single space (US-ASCII decimal 32). This function never splits multi-byte
    UTF-8 characters.
    """
    encoded = line.encode("utf-8")
    if len(encoded) <= max_octets:
        return line

    chunks: list[str] = []
    current_limit = max_octets
    current_bytes = bytearray()

    for char in line:
        char_bytes = char.encode("utf-8")
        if len(current_bytes) + len(char_bytes) > current_limit:
            if current_bytes:
                chunks.append(current_bytes.decode("utf-8"))
            current_bytes = bytearray(char_bytes)
            # Subsequent lines start with a single space (1 byte), so limit is 74
            current_limit = max_octets - 1
        else:
            current_bytes.extend(char_bytes)

    if current_bytes:
        chunks.append(current_bytes.decode("utf-8"))

    return "\r\n ".join(chunks)


def format_ics_line(name: str, value: str, params: str = "") -> str:
    """Format and fold an iCalendar property line."""
    if params:
        raw_line = f"{name};{params}:{value}"
    else:
        raw_line = f"{name}:{value}"
    return fold_line(raw_line)


def create_day_event(
    bs_date: BSDate,
    lang: str = "en",
    dtstamp: str = "20260101T000000Z",
) -> str:
    """Create a single VEVENT for a Bikram Sambat day."""
    greg_date = bs_date.gregorian_date
    next_day = greg_date + datetime.timedelta(days=1)

    start_str = greg_date.strftime("%Y%m%d")
    end_str = next_day.strftime("%Y%m%d")
    iso_date = greg_date.isoformat()
    uid = f"{iso_date}-{lang}@bs-calendar"

    summary_escaped = escape_ics_text(bs_date.summary(lang=lang))
    desc_escaped = escape_ics_text(bs_date.description())

    lines = [
        "BEGIN:VEVENT",
        format_ics_line("UID", uid),
        format_ics_line("DTSTAMP", dtstamp),
        format_ics_line("DTSTART", start_str, params="VALUE=DATE"),
        format_ics_line("DTEND", end_str, params="VALUE=DATE"),
        format_ics_line("SUMMARY", summary_escaped),
        format_ics_line("DESCRIPTION", desc_escaped),
        format_ics_line("TRANSP", "TRANSPARENT"),
        format_ics_line("STATUS", "CONFIRMED"),
        "END:VEVENT",
    ]
    return "\r\n".join(lines)


def create_holiday_event(
    holiday: Holiday,
    lang: str = "en",
    dtstamp: str = "20260101T000000Z",
) -> str:
    """Create a single VEVENT for an optional holiday."""
    greg_date = holiday.gregorian_date
    next_day = greg_date + datetime.timedelta(days=1)

    start_str = greg_date.strftime("%Y%m%d")
    end_str = next_day.strftime("%Y%m%d")
    iso_date = greg_date.isoformat()
    uid = f"holiday-{iso_date}-{lang}@bs-calendar"

    summary_text = holiday.summary(lang=lang)
    summary_escaped = escape_ics_text(summary_text)

    desc_parts = [
        f"Holiday: {holiday.name_en}",
        f"चाडपर्व: {holiday.name_ne}",
        f"BS: {holiday.bs_date_str}",
        f"Gregorian: {iso_date}",
    ]
    if holiday.description:
        desc_parts.append(holiday.description)
    desc_escaped = escape_ics_text("\n".join(desc_parts))

    lines = [
        "BEGIN:VEVENT",
        format_ics_line("UID", uid),
        format_ics_line("DTSTAMP", dtstamp),
        format_ics_line("DTSTART", start_str, params="VALUE=DATE"),
        format_ics_line("DTEND", end_str, params="VALUE=DATE"),
        format_ics_line("SUMMARY", summary_escaped),
        format_ics_line("DESCRIPTION", desc_escaped),
        format_ics_line("TRANSP", "TRANSPARENT"),
        format_ics_line("STATUS", "CONFIRMED"),
        "END:VEVENT",
    ]
    return "\r\n".join(lines)


def build_calendar_feed(
    dates: Iterable[BSDate],
    lang: str = "en",
    holidays: Sequence[Holiday] = (),
    dtstamp: str | None = None,
) -> str:
    """Build full RFC 5545 iCalendar string for the given dates."""
    if dtstamp is None:
        dtstamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    calname = CALNAME_NE if lang == "ne" else CALNAME_EN

    header_lines = [
        "BEGIN:VCALENDAR",
        format_ics_line("VERSION", VERSION),
        format_ics_line("PRODID", PRODID),
        format_ics_line("CALSCALE", CALSCALE),
        format_ics_line("METHOD", "PUBLISH"),
        format_ics_line("X-WR-CALNAME", escape_ics_text(calname)),
        format_ics_line("X-WR-TIMEZONE", TIMEZONE_STR),
        format_ics_line("X-PUBLISHED-TTL", PUBLISHED_TTL),
        format_ics_line("REFRESH-INTERVAL", REFRESH_INTERVAL, params="VALUE=DURATION"),
    ]

    event_blocks: list[str] = []

    # Map holidays by gregorian_date for inclusion alongside date events
    holiday_map: dict[datetime.date, list[Holiday]] = {}
    for h in holidays:
        holiday_map.setdefault(h.gregorian_date, []).append(h)

    for bs_date in dates:
        event_blocks.append(create_day_event(bs_date, lang=lang, dtstamp=dtstamp))
        for h in holiday_map.get(bs_date.gregorian_date, []):
            event_blocks.append(create_holiday_event(h, lang=lang, dtstamp=dtstamp))

    footer_lines = [
        "END:VCALENDAR",
        "",  # Ensures trailing CRLF
    ]

    all_blocks = header_lines + event_blocks + footer_lines
    return "\r\n".join(all_blocks)


def write_calendar_file(
    output_path: Path | str,
    dates: Iterable[BSDate],
    lang: str = "en",
    holidays: Sequence[Holiday] = (),
    dtstamp: str | None = None,
) -> Path:
    """Generate and write a calendar feed file to disk."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    ics_content = build_calendar_feed(
        dates=dates,
        lang=lang,
        holidays=holidays,
        dtstamp=dtstamp,
    )

    with open(path, "wb") as f:
        f.write(ics_content.encode("utf-8"))

    return path
