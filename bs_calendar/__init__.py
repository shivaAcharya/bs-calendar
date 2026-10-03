"""Subscribable Bikram Sambat (BS, Nepali) calendar feed generator."""

from bs_calendar.converter import (
    BSDate,
    DateOutOfRangeError,
    days_in_bs_month,
    from_bs,
    from_gregorian,
    get_current_bs_year,
    iter_bs_dates,
)
from bs_calendar.feed import (
    build_calendar_feed,
    create_day_event,
    escape_ics_text,
    fold_line,
    write_calendar_file,
)
from bs_calendar.holidays import Holiday, load_holidays

__version__ = "0.1.0"
__all__ = [
    "BSDate",
    "DateOutOfRangeError",
    "Holiday",
    "build_calendar_feed",
    "create_day_event",
    "days_in_bs_month",
    "escape_ics_text",
    "fold_line",
    "from_bs",
    "from_gregorian",
    "get_current_bs_year",
    "iter_bs_dates",
    "load_holidays",
    "write_calendar_file",
]
