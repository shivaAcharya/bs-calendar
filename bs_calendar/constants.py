"""Constants and configuration for Bikram Sambat calendar feed generator."""

from datetime import date
from typing import Mapping

# Supported BS and Gregorian bounds based on authoritative lookup data
MIN_BS_YEAR: int = 1975
MAX_BS_YEAR: int = 2100

MIN_AD_DATE: date = date(1918, 4, 13)
MAX_AD_DATE: date = date(2044, 4, 12)

# English month names (1-indexed, element 0 is None)
# Matches prompt specification:
# Baisakh, Jestha, Ashadh, Shrawan, Bhadra, Ashwin,
# Kartik, Mangsir, Poush, Magh, Falgun, Chaitra
MONTH_NAMES_EN: tuple[str | None, ...] = (
    None,
    "Baisakh",
    "Jestha",
    "Ashadh",
    "Shrawan",
    "Bhadra",
    "Ashwin",
    "Kartik",
    "Mangsir",
    "Poush",
    "Magh",
    "Falgun",
    "Chaitra",
)

# Devanagari month names (1-indexed)
MONTH_NAMES_NE: tuple[str | None, ...] = (
    None,
    "वैशाख",
    "जेष्ठ",
    "असार",
    "श्रावण",
    "भाद्र",
    "आश्विन",
    "कार्तिक",
    "मंसिर",
    "पौष",
    "माघ",
    "फाल्गुन",
    "चैत्र",
)

# Devanagari day of week names (0=Monday ... 6=Sunday, python weekday() convention)
DAY_NAMES_NE: Mapping[int, str] = {
    0: "सोमबार",
    1: "मङ्गलबार",
    2: "बुधबार",
    3: "बिहीबार",
    4: "शुक्रबार",
    5: "शनिबार",
    6: "आइतबार",
}

# Devanagari digits mapping
DEVANAGARI_DIGITS: Mapping[str, str] = {
    "0": "०",
    "1": "१",
    "2": "२",
    "3": "३",
    "4": "४",
    "5": "५",
    "6": "६",
    "7": "७",
    "8": "८",
    "9": "९",
}


def to_devanagari_number(val: int | str) -> str:
    """Convert an integer or numeric string to Devanagari numerals."""
    return "".join(DEVANAGARI_DIGITS.get(ch, ch) for ch in str(val))


# Calendar feed headers and metadata
PRODID: str = "-//Bikram Sambat Calendar//Nepali Date Feed//EN"
TIMEZONE_STR: str = "Asia/Kathmandu"
CALNAME_EN: str = "Nepali Date (BS)"
CALNAME_NE: str = "नेपाली मिति (वि.सं.)"
CALSCALE: str = "GREGORIAN"
VERSION: str = "2.0"
REFRESH_INTERVAL: str = "P1D"
PUBLISHED_TTL: str = "P1D"
