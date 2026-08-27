"""Shared parsing for canonical SSB dataset periods."""

from __future__ import annotations

import calendar
import re
from datetime import date
from datetime import datetime
from datetime import timedelta

_PeriodResult = tuple[str, date | tuple[int, ...]]

_MONTHS_PER_PERIOD = {"B": 2, "Q": 3, "T": 4, "H": 6}
_SSB_LIMITS = {
    period_format: 12 // months for period_format, months in _MONTHS_PER_PERIOD.items()
}
_CALENDAR_FORMATS = (
    ("year", r"\d{4}", "%Y"),
    ("month", r"\d{4}-\d{2}", "%Y-%m"),
    ("date", r"\d{4}-\d{2}-\d{2}", "%Y-%m-%d"),
)


def _try_calendar(period: str) -> _PeriodResult | None:
    for period_format, pattern, strptime_format in _CALENDAR_FORMATS:
        if re.fullmatch(pattern, period):
            try:
                parsed_date = datetime.strptime(  # noqa: DTZ007 - date-only input
                    period, strptime_format
                ).date()
            except ValueError:
                return None
            else:
                return period_format, parsed_date
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
        datetime(  # noqa: DTZ001 - timezone is not part of the period format
            *components[:6], microsecond=components[6] * 1000
        )
    except ValueError:
        return None
    return "datetime", components


def _try_ssb(period: str) -> _PeriodResult | None:
    match = re.fullmatch(r"(\d{4})-([BQTH])(\d)", period)
    if not match:
        return None
    year, kind, number = int(match.group(1)), match.group(2), int(match.group(3))
    if 1 <= year <= 9999 and 1 <= number <= _SSB_LIMITS[kind]:
        return kind, (year, number)
    return None


_PARSERS = (
    _try_calendar,
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


def _month_range(year: int, start_month: int, end_month: int) -> tuple[date, date]:
    last_day = calendar.monthrange(year, end_month)[1]
    return date(year, start_month, 1), date(year, end_month, last_day)


def period_date_range(period: str) -> tuple[date, date]:
    """Return the first and last calendar dates represented by a period."""
    period_format, value = parse_period(period)

    match period_format:
        case "date" | "datetime":
            d = value if isinstance(value, date) else date(*value[:3])
            return d, d
        case "week":
            return value, value + timedelta(days=6)
        case "month":
            return _month_range(value.year, value.month, value.month)
        case "year":
            return value, date(value.year, 12, 31)
        case "ordinal":
            year, day_of_year = value
            start = date(year, 1, 1) + timedelta(days=day_of_year - 1)
            return start, start
        case _:
            year, period_index = value
            months = _MONTHS_PER_PERIOD[period_format]
            start_month = (period_index - 1) * months + 1
            return _month_range(year, start_month, start_month + months - 1)


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
