"""Shared parsing for canonical SSB dataset periods.

This module builds on ``arrow`` for date validation and arithmetic,
consistent with ``dapla_dataset_path_info.py``. Unlike that module's more
permissive legacy formats, this module first enforces a strict canonical
syntax (via its own regexes, requiring separators such as ``-``) before
handing the matched value off to ``arrow`` for validation and date-range
calculation.
"""

from __future__ import annotations

import re
from datetime import date
from typing import cast

import arrow

_PeriodResult = tuple[str, date | tuple[int, ...]]

_MONTHS_PER_PERIOD = {"B": 2, "Q": 3, "T": 4, "H": 6}
# fmt: off
_SSB_LIMITS = {
    period_format: 12 // months
    for period_format, months in _MONTHS_PER_PERIOD.items()
}
# fmt: on
_CALENDAR_FORMATS = (
    ("year", re.compile(r"\d{4}"), "YYYY"),
    ("month", re.compile(r"\d{4}-\d{2}"), "YYYY-MM"),
    ("date", re.compile(r"\d{4}-\d{2}-\d{2}"), "YYYY-MM-DD"),
)
_WEEK_PATTERN = re.compile(r"(\d{4})-W(\d{2})")
_WEEK_ARROW_PATTERN = "W"
_ORDINAL_PATTERN = re.compile(r"(\d{4})-(\d{3})")
_ORDINAL_ARROW_PATTERN = "YYYY-DDD"
_DATETIME_PATTERN = re.compile(
    r"(\d{4})-(\d{2})-(\d{2})T(\d{2})-(\d{2})-(\d{2})\.(\d{3})"
)
_DATETIME_ARROW_PATTERN = "YYYY-MM-DDTHH-mm-ss.SSS"
_SSB_PATTERN = re.compile(r"(\d{4})-([BQTH])(\d)")


class _UnsupportedPeriodFormatError(Exception):
    """A parsed period format has no date-range implementation.

    Signals a bug: a parser was added to ``_PARSERS`` without a matching case
    in ``_date_range``. Deliberately not a ``ValueError`` so that it is not
    reported to callers as invalid input.
    """


def _try_calendar(period: str) -> _PeriodResult | None:
    """Parse a valid calendar year, month, or date.

    Return the calendar format and its first represented date, or ``None``
    when the value has an unsupported format or is not a valid calendar date.
    """
    for period_format, pattern, arrow_pattern in _CALENDAR_FORMATS:
        if not pattern.fullmatch(period):
            continue
        try:
            parsed_date = arrow.get(period, arrow_pattern).date()
        except ValueError:
            return None
        return period_format, parsed_date
    return None


def _try_week(period: str) -> _PeriodResult | None:
    """Parse a valid ISO week and return the date of its Monday.

    Return ``None`` when the value is not an ISO week or identifies a week
    that does not exist.
    """
    if not _WEEK_PATTERN.fullmatch(period):
        return None
    try:
        parsed_date = arrow.get(period, _WEEK_ARROW_PATTERN).date()
    except ValueError:
        return None
    return "week", parsed_date


def _try_ordinal(period: str) -> _PeriodResult | None:
    """Parse a valid ordinal year and day, returning the represented date.

    Return ``None`` when the value is not an ordinal period or the day does
    not exist in the given year.
    """
    match = _ORDINAL_PATTERN.fullmatch(period)
    if not match:
        return None
    try:
        parsed_date = arrow.get(period, _ORDINAL_ARROW_PATTERN).date()
    except ValueError:
        return None
    year = int(match.group(1))
    if parsed_date.year != year:
        return None
    return "ordinal", parsed_date


def _try_datetime(period: str) -> _PeriodResult | None:
    """Parse a valid date and time into its numeric components.

    The returned tuple contains year, month, day, hour, minute, second, and
    millisecond. Return ``None`` for an unsupported or invalid datetime.
    """
    match = _DATETIME_PATTERN.fullmatch(period)
    if not match:
        return None
    components = tuple(map(int, match.groups()))
    year, month, day = components[:3]
    try:
        parsed = arrow.get(period, _DATETIME_ARROW_PATTERN)
    except ValueError:
        return None
    # Reject ISO8601's "24:00:00 = midnight at the start of the next day"
    # special case, which arrow accepts and rolls over to the next day.
    if (parsed.year, parsed.month, parsed.day) != (year, month, day):
        return None
    return "datetime", components


def _try_ssb(period: str) -> _PeriodResult | None:
    """Parse a valid SSB period into its kind, year, and period number.

    Supported kinds are bimonthly (``B``), quarterly (``Q``), four-monthly
    (``T``), and half-yearly (``H``). Return ``None`` for invalid values.
    """
    match = _SSB_PATTERN.fullmatch(period)
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
    """Parse and validate a canonical period string.

    Return the detected format together with a date or tuple containing the
    parsed value.

    Raises:
        ValueError: If the period does not use a supported format or contains
            an invalid date or period number.
    """
    for parser in _PARSERS:
        result = parser(period)
        if result is not None:
            return result
    msg = f"Invalid period: {period}"
    raise ValueError(msg)


def _ssb_month_range(year: int, start_month: int, end_month: int) -> tuple[date, date]:
    """Return the inclusive date range spanning two months in one year."""
    start = arrow.Arrow(year, start_month, 1)
    end = arrow.Arrow(year, end_month, 1)
    return start.floor("month").date(), end.ceil("month").date()


def _date_range(period_format: str, value: date | tuple[int, ...]) -> tuple[date, date]:
    """Return the inclusive date range for an already parsed period.

    Raises:
        _UnsupportedPeriodFormatError: If the format has no implementation here.
    """
    match period_format:
        case "date" | "datetime" | "ordinal":
            d = value if isinstance(value, date) else date(*value[:3])
            return d, d
        case "week":
            week_value = cast("date", value)
            week_arrow = arrow.Arrow.fromdate(week_value)
            return week_arrow.floor("week").date(), week_arrow.ceil("week").date()
        case "month":
            month_value = cast("date", value)
            month_arrow = arrow.Arrow.fromdate(month_value)
            return month_arrow.floor("month").date(), month_arrow.ceil("month").date()
        case "year":
            year_value = cast("date", value)
            year_arrow = arrow.Arrow.fromdate(year_value)
            return year_arrow.floor("year").date(), year_arrow.ceil("year").date()
        case "B" | "Q" | "T" | "H":
            year, period_index = cast("tuple[int, ...]", value)
            months = _MONTHS_PER_PERIOD[period_format]
            start_month = (period_index - 1) * months + 1
            return _ssb_month_range(year, start_month, start_month + months - 1)
        case _:
            raise _UnsupportedPeriodFormatError(period_format)


def period_date_range(period: str) -> tuple[date, date]:
    """Return the inclusive calendar date range represented by a period.

    Raises:
        ValueError: If the period is invalid, unsupported, or its date range
            falls outside the range representable by ``datetime.date``.
    """
    period_format, value = parse_period(period)
    try:
        return _date_range(period_format, value)
    except (ValueError, OverflowError) as exc:
        msg = f"Invalid period: {period}"
        raise ValueError(msg) from exc


def validate_period_range(
    period_from: str,
    period_to: str | None = None,
) -> None:
    """Validate one period or an inclusive range of canonical periods.

    When an end period is supplied, both periods must use the same format and
    the start must not follow the end. Period values must omit the ``p`` path
    prefix.

    Raises:
        ValueError: If a period is invalid, uses the ``p`` prefix, differs in
            format from the other period, or occurs out of chronological order.
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
    # from_value and to_value are guaranteed to be the same concrete type
    # here (both `date` or both `tuple[int, ...]`) because from_format ==
    # to_format was already checked above, so this comparison is safe despite
    # the `date | tuple[int, ...]` union type.
    if from_value > to_value:  # type: ignore[operator]
        msg = "periods must be in chronological order"
        raise ValueError(msg)
