"""Date conversion between Gregorian (AD) and Bikram Sambat (BS) calendars."""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Iterator

import nepali_datetime

from bs_calendar.constants import (
    DAY_NAMES_NE,
    MAX_AD_DATE,
    MAX_BS_YEAR,
    MIN_AD_DATE,
    MIN_BS_YEAR,
    MONTH_NAMES_EN,
    MONTH_NAMES_NE,
    to_devanagari_number,
)


class DateOutOfRangeError(ValueError):
    """Raised when a date falls outside the supported Bikram Sambat range."""


@dataclass(frozen=True)
class BSDate:
    """Represents a Bikram Sambat (BS) date linked to its Gregorian counterpart."""

    year: int
    month: int
    day: int
    gregorian_date: datetime.date

    def __post_init__(self) -> None:
        if not (MIN_BS_YEAR <= self.year <= MAX_BS_YEAR):
            raise DateOutOfRangeError(
                f"BS year {self.year} is out of supported range ({MIN_BS_YEAR}..{MAX_BS_YEAR} BS)."
            )
        if not (1 <= self.month <= 12):
            raise ValueError(f"BS month must be in 1..12, got {self.month}.")
        max_days = days_in_bs_month(self.year, self.month)
        if not (1 <= self.day <= max_days):
            raise ValueError(
                f"BS day must be in 1..{max_days} for year {self.year}, month {self.month}; got {self.day}."
            )

    @property
    def month_name_en(self) -> str:
        """English month name (e.g., 'Ashwin')."""
        name = MONTH_NAMES_EN[self.month]
        assert name is not None
        return name

    @property
    def month_name_ne(self) -> str:
        """Nepali Devanagari month name (e.g., 'आश्विन')."""
        name = MONTH_NAMES_NE[self.month]
        assert name is not None
        return name

    @property
    def is_month_start(self) -> bool:
        """True if this is the first day of the BS month."""
        return self.day == 1

    @property
    def is_year_start(self) -> bool:
        """True if this is the first day of the BS year (New Year, 1 Baisakh)."""
        return self.month == 1 and self.day == 1

    def summary(self, lang: str = "en") -> str:
        """Return the event summary (title) according to language requirements.

        - English (en):
          First day of month: 'Month Day, Year' (e.g. 'Ashwin 1, 2083')
          Other days: 'Month Day' (e.g. 'Ashwin 17')

        - Nepali (ne):
          First day of month: 'महिना गते, वर्ष' (e.g. 'आश्विन १, २०८३')
          Other days: 'महिना गते' (e.g. 'आश्विन १७')
        """
        if lang == "ne":
            day_str = to_devanagari_number(self.day)
            year_str = to_devanagari_number(self.year)
            if self.is_month_start:
                return f"{self.month_name_ne} {day_str}, {year_str}"
            return f"{self.month_name_ne} {day_str}"

        # Default to English
        if self.is_month_start:
            return f"{self.month_name_en} {self.day}, {self.year}"
        return f"{self.month_name_en} {self.day}"

    def format_bs_en(self) -> str:
        """Formatted full BS date in English (e.g., 'Ashwin 17, 2083')."""
        return f"{self.month_name_en} {self.day}, {self.year}"

    def format_bs_ne(self) -> str:
        """Formatted full BS date in Devanagari (e.g., 'आश्विन १७, २०८३')."""
        return (
            f"{self.month_name_ne} {to_devanagari_number(self.day)}, "
            f"{to_devanagari_number(self.year)}"
        )

    def format_ad(self) -> str:
        """Formatted Gregorian date (e.g., 'Saturday, October 3, 2026')."""
        # Format weekday and full date
        weekday_name = self.gregorian_date.strftime("%A")
        month_name = self.gregorian_date.strftime("%B")
        return f"{weekday_name}, {month_name} {self.gregorian_date.day}, {self.gregorian_date.year}"

    def description(self) -> str:
        """Return multi-line full date description for calendar event.

        Includes BS date in English and Nepali, plus the Gregorian date.
        """
        day_ne = DAY_NAMES_NE[self.gregorian_date.weekday()]
        return (
            f"Bikram Sambat: {self.format_bs_en()}\n"
            f"नेपाली मिति: {self.format_bs_ne()} ({day_ne})\n"
            f"Gregorian: {self.format_ad()} ({self.gregorian_date.isoformat()})"
        )


def days_in_bs_month(year: int, month: int) -> int:
    """Return the number of days in the specified BS month and year."""
    if not (MIN_BS_YEAR <= year <= MAX_BS_YEAR):
        raise DateOutOfRangeError(
            f"BS year {year} is out of supported range ({MIN_BS_YEAR}..{MAX_BS_YEAR} BS)."
        )
    if not (1 <= month <= 12):
        raise ValueError(f"BS month must be in 1..12, got {month}.")
    return nepali_datetime._days_in_month(year, month)


def from_gregorian(d: datetime.date) -> BSDate:
    """Convert a Gregorian (AD) date to a BSDate instance."""
    if not (MIN_AD_DATE <= d <= MAX_AD_DATE):
        raise DateOutOfRangeError(
            f"Gregorian date {d} is outside the supported Bikram Sambat conversion range "
            f"({MIN_AD_DATE.isoformat()} to {MAX_AD_DATE.isoformat()})."
        )
    try:
        bs_dt = nepali_datetime.date.from_datetime_date(d)
        return BSDate(
            year=bs_dt.year,
            month=bs_dt.month,
            day=bs_dt.day,
            gregorian_date=d,
        )
    except Exception as exc:
        raise DateOutOfRangeError(
            f"Failed to convert Gregorian date {d} to Bikram Sambat: {exc}"
        ) from exc


def from_bs(year: int, month: int, day: int) -> BSDate:
    """Convert a Bikram Sambat date to a BSDate instance."""
    if not (MIN_BS_YEAR <= year <= MAX_BS_YEAR):
        raise DateOutOfRangeError(
            f"BS year {year} is out of supported range ({MIN_BS_YEAR}..{MAX_BS_YEAR} BS)."
        )
    if not (1 <= month <= 12):
        raise ValueError(f"BS month must be in 1..12, got {month}.")
    max_days = days_in_bs_month(year, month)
    if not (1 <= day <= max_days):
        raise ValueError(
            f"BS day must be in 1..{max_days} for year {year}, month {month}; got {day}."
        )
    try:
        bs_dt = nepali_datetime.date(year, month, day)
        gregorian_d = bs_dt.to_datetime_date()
        return BSDate(
            year=year,
            month=month,
            day=day,
            gregorian_date=gregorian_d,
        )
    except Exception as exc:
        if isinstance(exc, (DateOutOfRangeError, ValueError)):
            raise
        raise ValueError(f"Invalid Bikram Sambat date {year}-{month:02d}-{day:02d}: {exc}") from exc


def get_current_bs_year(today: datetime.date | None = None) -> int:
    """Return the current Bikram Sambat year based on current Gregorian date."""
    if today is None:
        today = datetime.date.today()
    return from_gregorian(today).year


def iter_bs_dates(start_year: int, num_years: int = 3) -> Iterator[BSDate]:
    """Iterate through all BS dates sequentially for `num_years` full BS years.

    Begins at 1 Baisakh of `start_year` and ends on the final day of Chaitra
    in `start_year + num_years - 1`.
    """
    if num_years < 1:
        raise ValueError(f"num_years must be at least 1, got {num_years}.")

    end_year = start_year + num_years - 1

    if not (MIN_BS_YEAR <= start_year <= MAX_BS_YEAR):
        raise DateOutOfRangeError(
            f"Start BS year {start_year} is outside supported range ({MIN_BS_YEAR}..{MAX_BS_YEAR})."
        )
    if not (MIN_BS_YEAR <= end_year <= MAX_BS_YEAR):
        raise DateOutOfRangeError(
            f"End BS year {end_year} exceeds maximum supported range ({MIN_BS_YEAR}..{MAX_BS_YEAR})."
        )

    # First BS date in the range
    first_bs = from_bs(start_year, 1, 1)
    # Last BS date in the range
    last_month_days = days_in_bs_month(end_year, 12)
    last_bs = from_bs(end_year, 12, last_month_days)

    cur_ad = first_bs.gregorian_date
    end_ad = last_bs.gregorian_date
    one_day = datetime.timedelta(days=1)

    while cur_ad <= end_ad:
        yield from_gregorian(cur_ad)
        cur_ad += one_day
