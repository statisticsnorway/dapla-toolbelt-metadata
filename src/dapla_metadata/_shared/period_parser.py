"""Shared parsing for canonical SSB dataset periods."""

from __future__ import annotations

import calendar
import re
from datetime import date
from datetime import timedelta

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
    match = re.fullmatch(r"(\d{4})-(\d{2})", period)
    if not match:
        return None
    try:
        return "month", date(int(match.group(1)), int(match.group(2)), 1)
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
    match = re.fullmatch(r"(\d{4})-W(\d{2})", period)
    if not match:
        return None
    try:
        return "week", date.fromisocalendar(int(match.group(1)), int(match.group(2)), 1)
    except ValueError:
        return None


def _try_ordinal(period: str) -> _PeriodResult | None:
    match = re.fullmatch(r"(\d{4})-(\d{3})", period)
    if not match:
        return None
    year, ordinal = int(match.group(1)), int(match.group(2))
    if 1 <= year <= 9999 and 1 <= ordinal <= 365 + calendar.isleap(year):
        return "ordinal", (year, ordinal)
    return None


def _try_datetime(period: str) -> _PeriodResult | None:
    match = re.fullmatch(
        r"(\d{4})-(\d{2})-(\d{2})T(\d{2})-(\d{2})-(\d{2})\.(\d{3})",
        period,
    )
    if not match:
        return None
    components = tuple(map(int, match.groups()))
    try:
        date(*components[:3])
    except ValueError:
        return None
    if components[3] < 24 and components[4] < 60 and components[5] < 60:
        return "datetime", components
    return None


def _try_ssb(period: str) -> _PeriodResult | None:
    match = re.fullmatch(r"(\d{4})-([BQTH])(\d)", period)
    if not match:
        return None
    year, kind, number = int(match.group(1)), match.group(2), int(match.group(3))
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
    """Parse and validate a canonical period string."""
    for parser in _PARSERS:
        result = parser(period)
        if result is not None:
            return result
    msg = f"Invalid period: {period}"
    raise ValueError(msg)


def period_date_range(period: str) -> tuple[date, date]:  # noqa: PLR0911
    """Return the first and last calendar dates represented by a period."""
    period_format, value = parse_period(period)

    if isinstance(value, date):
        if period_format == "year":
            return value, date(value.year, 12, 31)
        if period_format == "month":
            last_day = calendar.monthrange(value.year, value.month)[1]
            return value, date(value.year, value.month, last_day)
        if period_format == "week":
            return value, value + timedelta(days=6)
        return value, value

    year = value[0]
    if period_format == "ordinal":
        ordinal_date = date(year, 1, 1) + timedelta(days=value[1] - 1)
        return ordinal_date, ordinal_date
    if period_format == "datetime":
        datetime_date = date(*value[:3])
        return datetime_date, datetime_date

    months_per_period = {"B": 2, "Q": 3, "T": 4, "H": 6}[period_format]
    start_month = (value[1] - 1) * months_per_period + 1
    end_month = start_month + months_per_period - 1
    return (
        date(year, start_month, 1),
        date(year, end_month, calendar.monthrange(year, end_month)[1]),
    )


def validate_period_range(
    period_from: str,
    period_to: str | None = None,
) -> None:
    """Validate canonical periods for matching formats and chronological order."""
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
