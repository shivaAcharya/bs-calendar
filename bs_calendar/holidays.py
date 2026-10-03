"""Support for optional external holiday definitions (data/holidays.json)."""

from __future__ import annotations

import datetime
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from bs_calendar.converter import from_bs, from_gregorian

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Holiday:
    """Represents a holiday entry that can be rendered into the calendar feed."""

    gregorian_date: datetime.date
    bs_date_str: str
    name_en: str
    name_ne: str
    description: str | None = None

    def summary(self, lang: str = "en") -> str:
        """Return holiday title in chosen language."""
        if lang == "ne" and self.name_ne:
            return self.name_ne
        return self.name_en or self.name_ne


def parse_holiday_entry(entry: dict[str, Any]) -> Holiday | None:
    """Parse a single JSON holiday entry into a Holiday dataclass."""
    name_en = entry.get("name_en") or entry.get("name", "")
    name_ne = entry.get("name_ne") or entry.get("name", "")
    description = entry.get("description")

    gregorian_raw = entry.get("gregorian_date") or entry.get("date_ad")
    bs_raw = entry.get("bs_date") or entry.get("date_bs")

    greg_date: datetime.date | None = None
    bs_str: str = ""

    if gregorian_raw:
        try:
            greg_date = datetime.date.fromisoformat(str(gregorian_raw).strip())
        except ValueError:
            logger.warning("Invalid gregorian_date format: %s", gregorian_raw)

    if bs_raw and not greg_date:
        # Convert from BS to Gregorian
        try:
            parts = [int(p) for p in str(bs_raw).strip().split("-")]
            if len(parts) == 3:
                bs_obj = from_bs(parts[0], parts[1], parts[2])
                greg_date = bs_obj.gregorian_date
                bs_str = f"{bs_obj.year:04d}-{bs_obj.month:02d}-{bs_obj.day:02d}"
        except Exception as exc:
            logger.warning("Failed to parse bs_date '%s': %s", bs_raw, exc)

    if greg_date is None:
        logger.warning("Skipping holiday entry without valid date: %s", entry)
        return None

    if not bs_str:
        try:
            bs_obj = from_gregorian(greg_date)
            bs_str = f"{bs_obj.year:04d}-{bs_obj.month:02d}-{bs_obj.day:02d}"
        except Exception:
            bs_str = ""

    return Holiday(
        gregorian_date=greg_date,
        bs_date_str=bs_str,
        name_en=str(name_en).strip(),
        name_ne=str(name_ne).strip(),
        description=str(description).strip() if description else None,
    )


def load_holidays(path: Path | str | None = None) -> list[Holiday]:
    """Load holidays from a JSON file if present.

    Returns an empty list if the file is not found or path is None.
    """
    if path is None:
        path = Path("data/holidays.json")
    else:
        path = Path(path)

    if not path.is_file():
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except Exception as exc:
        logger.warning("Failed to read holidays file %s: %s", path, exc)
        return []

    if not isinstance(raw_data, list):
        logger.warning("Holidays JSON root must be a list, got %s", type(raw_data))
        return []

    holidays: list[Holiday] = []
    for item in raw_data:
        if isinstance(item, dict):
            holiday = parse_holiday_entry(item)
            if holiday:
                holidays.append(holiday)

    return holidays
