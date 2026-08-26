# Copyright (c) 2026 Statistics Norway
"""Canonical period-string parser used by dataset-path validation."""

from __future__ import annotations

import calendar
import re
from datetime import date

_PeriodResult = tuple[str, date | tuple[int, ...]]

_SSB_LIMITS: dict[str, int] = {"B": 6, "Q": 4, "T": 3, "H": 2}


def _try_year(period: str) -> _PeriodResult | None:
    if not re.fullmatch(r"\d{4}", period):
        return None
    try:
        return "year", date(int(period), 1, 1)
    except ValueError:
        return None


def _try_month(period: str) -> _PeriodResult | None:
    m = re.fullmatch(r"(\d{4})-(\d{2})", period)
    if not m:
        return None
    try:
        return "month", date(int(m.group(1)), int(m.group(2)), 1)
    except ValueError:
        return None


def _try_date(period: str) -> _PeriodResult | None:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", period):
        return None
    try:
        return "date", date.fromisoformat(period)
    except ValueError:
        return None


def _try_week(period: str) -> _PeriodResult | None:
    m = re.fullmatch(r"(\d{4})-W(\d{2})", period)
    if not m:
        return None
    try:
        return "week", date.fromisocalendar(int(m.group(1)), int(m.group(2)), 1)
    except ValueError:
        return None


def _try_ordinal(period: str) -> _PeriodResult | None:
    m = re.fullmatch(r"(\d{4})-(\d{3})", period)
    if not m:
        return None
    year, ordinal = int(m.group(1)), int(m.group(2))
    if 1 <= year <= 9999 and 1 <= ordinal <= 365 + calendar.isleap(year):
        return "ordinal", (year, ordinal)
    return None


def _try_datetime(period: str) -> _PeriodResult | None:
    m = re.fullmatch(
        r"(\d{4})-(\d{2})-(\d{2})T(\d{2})-(\d{2})-(\d{2})\.(\d{3})",
        period,
    )
    if not m:
        return None
    components = tuple(map(int, m.groups()))
    try:
        date(*components[:3])
    except ValueError:
        return None
    if components[3] < 24 and components[4] < 60 and components[5] < 60:
        return "datetime", components
    return None


def _try_ssb(period: str) -> _PeriodResult | None:
    m = re.fullmatch(r"(\d{4})-([BQTH])(\d)", period)
    if not m:
        return None
    year, kind, number = int(m.group(1)), m.group(2), int(m.group(3))
    if 1 <= year <= 9999 and 1 <= number <= _SSB_LIMITS[kind]:
        return kind, (year, number)
    return None


_PARSERS = (
    _try_year,
    _try_month,
    _try_date,
    _try_week,
    _try_ordinal,
    _try_datetime,
    _try_ssb,
)


def parse_period(period: str) -> _PeriodResult:
    """Parse and validate a canonical period string.

    Supported formats match the SSB dataset-naming standard:

    * year: ``YYYY``
    * month: ``YYYY-MM``
    * calendar date: ``YYYY-MM-DD``
    * ISO week: ``YYYY-Www``
    * ISO ordinal date: ``YYYY-DDD``
    * date and time: ``YYYY-MM-DDTHH-MM-SS.sss``
    * SSB bimonthly: ``YYYY-Bn`` (n 1-6)
    * SSB quarterly: ``YYYY-Qn`` (n 1-4)
    * SSB four-month: ``YYYY-Tn`` (n 1-3)
    * SSB half-year: ``YYYY-Hn`` (n 1-2)

    Args:
        period: A period string without the ``p`` prefix.

    Returns:
        A ``(format_name, comparable_value)`` tuple. ``comparable_value``
        supports ``<`` / ``>`` ordering within the same format.

    Raises:
        ValueError: If the string does not match any supported format.
    """
    for parser in _PARSERS:
        result = parser(period)
        if result is not None:
            return result
    msg = f"Invalid period: {period}"
    raise ValueError(msg)


def validate_period_range(
    period_from: str,
    period_to: str | None = None,
) -> None:
    """Validate a period string or an ordered pair of period strings.

    Checks the ``p`` prefix, format validity, matching formats, and
    chronological order.  Type checking is the caller's responsibility.

    Args:
        period_from: The start period string, without the ``p`` prefix.
        period_to: An optional end period string, without the ``p`` prefix.

    Raises:
        ValueError: If either period has the ``p`` prefix, fails format
            validation, uses a different format, or is out of order.
    """
    if period_from.startswith("p") or (
        period_to is not None and period_to.startswith("p")
    ):
        msg = "periods must not include the 'p' prefix"
        raise ValueError(msg)

    from_format, from_value = parse_period(period_from)
    if period_to is None:
        return

    to_format, to_value = parse_period(period_to)
    if from_format != to_format:
        msg = "periods must use the same format"
        raise ValueError(msg)
    if from_value > to_value:
        msg = "periods must be in chronological order"
        raise ValueError(msg)
