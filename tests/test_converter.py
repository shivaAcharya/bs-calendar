"""Unit tests for Bikram Sambat date conversion, boundaries, and formatting."""

import datetime
import pytest

from bs_calendar.constants import (
    MAX_AD_DATE,
    MAX_BS_YEAR,
    MIN_AD_DATE,
    MIN_BS_YEAR,
    MONTH_NAMES_EN,
    MONTH_NAMES_NE,
    to_devanagari_number,
)
from bs_calendar.converter import (
    BSDate,
    DateOutOfRangeError,
    days_in_bs_month,
    from_bs,
    from_gregorian,
    get_current_bs_year,
    iter_bs_dates,
)


class TestAnchorDates:
    """Verify known anchor dates from authoritative official Nepali Patro records."""

    @pytest.mark.parametrize(
        ("bs_year", "bs_month", "bs_day", "expected_ad", "expected_weekday"),
        [
            # Nepali New Year 2082 (official anchor from prompt)
            (2082, 1, 1, datetime.date(2025, 4, 14), "Monday"),
            # Nepali New Year 2081 (official)
            (2081, 1, 1, datetime.date(2024, 4, 13), "Saturday"),
            # Nepali New Year 2080 (official)
            (2080, 1, 1, datetime.date(2023, 4, 14), "Friday"),
            # Nepali New Year 2083 (official)
            (2083, 1, 1, datetime.date(2026, 4, 14), "Tuesday"),
            # Nepali New Year 2078 (official)
            (2078, 1, 1, datetime.date(2021, 4, 14), "Wednesday"),
            # Boundary min anchor (1975-01-01 BS)
            (1975, 1, 1, datetime.date(1918, 4, 13), "Saturday"),
            # Boundary max anchor (2100-12-30 BS)
            (2100, 12, 30, datetime.date(2044, 4, 12), "Tuesday"),
        ],
    )
    def test_anchor_from_bs(
        self,
        bs_year: int,
        bs_month: int,
        bs_day: int,
        expected_ad: datetime.date,
        expected_weekday: str,
    ) -> None:
        bs_date = from_bs(bs_year, bs_month, bs_day)
        assert bs_date.gregorian_date == expected_ad
        assert bs_date.gregorian_date.strftime("%A") == expected_weekday

        # Verify round-trip conversion from Gregorian back to BS
        back_bs = from_gregorian(expected_ad)
        assert back_bs.year == bs_year
        assert back_bs.month == bs_month
        assert back_bs.day == bs_day


class TestMonthBoundariesAndRollovers:
    """Test transitions at the edges of months and year rollovers."""

    def test_month_transition_within_year(self) -> None:
        # Ashwin in 2083 has 31 days
        ashwin_days = days_in_bs_month(2083, 6)
        assert ashwin_days in (30, 31, 32)

        last_ashwin = from_bs(2083, 6, ashwin_days)
        first_kartik = from_bs(2083, 7, 1)

        # Gregorian dates must be consecutive
        assert first_kartik.gregorian_date - last_ashwin.gregorian_date == datetime.timedelta(days=1)

    def test_year_rollover(self) -> None:
        # Chaitra is month 12
        for year in (2079, 2080, 2081, 2082, 2083):
            chaitra_days = days_in_bs_month(year, 12)
            last_day_year = from_bs(year, 12, chaitra_days)
            first_day_next_year = from_bs(year + 1, 1, 1)

            assert first_day_next_year.gregorian_date - last_day_year.gregorian_date == datetime.timedelta(
                days=1
            )
            assert first_day_next_year.is_year_start is True
            assert last_day_year.is_year_start is False

    def test_gregorian_leap_year_handling(self) -> None:
        # 2024 is a Gregorian leap year (Feb 29 exists)
        leap_ad = datetime.date(2024, 2, 29)
        bs_date = from_gregorian(leap_ad)
        # 2024-02-29 corresponds to Falgun 17, 2080 BS
        assert bs_date.year == 2080
        assert bs_date.month == 11
        assert bs_date.day == 17
        assert from_bs(2080, 11, 17).gregorian_date == leap_ad


class TestDateOutOfRangeErrors:
    """Ensure clear errors are raised when dates exceed covered range."""

    def test_bs_year_below_min_raises(self) -> None:
        with pytest.raises(DateOutOfRangeError, match=r"out of supported range"):
            from_bs(MIN_BS_YEAR - 1, 1, 1)

    def test_bs_year_above_max_raises(self) -> None:
        with pytest.raises(DateOutOfRangeError, match=r"out of supported range"):
            from_bs(MAX_BS_YEAR + 1, 1, 1)

    def test_gregorian_date_below_min_raises(self) -> None:
        too_early = MIN_AD_DATE - datetime.timedelta(days=1)
        with pytest.raises(DateOutOfRangeError, match=r"outside the supported"):
            from_gregorian(too_early)

    def test_gregorian_date_above_max_raises(self) -> None:
        too_late = MAX_AD_DATE + datetime.timedelta(days=1)
        with pytest.raises(DateOutOfRangeError, match=r"outside the supported"):
            from_gregorian(too_late)

    def test_invalid_month_or_day_raises(self) -> None:
        with pytest.raises(ValueError, match=r"BS month must be in 1\.\.12"):
            from_bs(2083, 13, 1)

        with pytest.raises(ValueError, match=r"BS day must be in"):
            from_bs(2083, 1, 35)


class TestFormattingAndSummaries:
    """Verify event summary (title) rules and description contents."""

    def test_month_start_summary_includes_year(self) -> None:
        bs_date = from_bs(2083, 6, 1)  # Ashwin 1, 2083
        assert bs_date.is_month_start is True
        assert bs_date.summary("en") == "Ashwin 1, 2083"
        assert bs_date.summary("ne") == "आश्विन १, २०८३"

    def test_regular_day_summary_excludes_year(self) -> None:
        bs_date = from_bs(2083, 6, 17)  # Ashwin 17
        assert bs_date.is_month_start is False
        assert bs_date.summary("en") == "Ashwin 17"
        assert bs_date.summary("ne") == "आश्विन १७"

    def test_english_month_names_match_prompt(self) -> None:
        expected_months = [
            "Baisakh", "Jestha", "Ashadh", "Shrawan", "Bhadra", "Ashwin",
            "Kartik", "Mangsir", "Poush", "Magh", "Falgun", "Chaitra",
        ]
        actual_months = [MONTH_NAMES_EN[m] for m in range(1, 13)]
        assert actual_months == expected_months

    def test_devanagari_numerals(self) -> None:
        assert to_devanagari_number(0) == "०"
        assert to_devanagari_number(17) == "१७"
        assert to_devanagari_number(2083) == "२०८३"

    def test_description_contains_required_elements(self) -> None:
        bs_date = from_bs(2083, 6, 17)
        desc = bs_date.description()
        # Must contain BS date in English
        assert "Ashwin 17, 2083" in desc
        # Must contain BS date in Nepali
        assert "आश्विन १७, २०८३" in desc
        # Must contain Gregorian date
        assert "October" in desc
        assert "2026" in desc


class TestIteration:
    """Test date generator iter_bs_dates."""

    def test_one_full_bs_year_count(self) -> None:
        dates = list(iter_bs_dates(start_year=2082, num_years=1))
        # A normal BS year is either 365 or 366 days
        assert len(dates) in (365, 366)
        assert dates[0].month == 1 and dates[0].day == 1
        assert dates[-1].month == 12

    def test_consecutive_days_without_gaps(self) -> None:
        dates = list(iter_bs_dates(start_year=2082, num_years=2))
        for i in range(len(dates) - 1):
            diff = dates[i + 1].gregorian_date - dates[i].gregorian_date
            assert diff == datetime.timedelta(days=1), f"Gap found between {dates[i]} and {dates[i+1]}"

    def test_current_bs_year_detection(self) -> None:
        # 2026-10-03 is in BS 2083
        current = get_current_bs_year(today=datetime.date(2026, 10, 3))
        assert current == 2083
