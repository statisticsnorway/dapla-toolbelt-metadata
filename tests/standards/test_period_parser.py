from datetime import date

import pytest

from dapla_metadata._shared.period_parser import parse_period
from dapla_metadata._shared.period_parser import period_date_range


@pytest.mark.parametrize(
    ("period", "expected"),
    [
        ("2024", ("year", date(2024, 1, 1))),
        ("2024-02", ("month", date(2024, 2, 1))),
        ("2024-02-29", ("date", date(2024, 2, 29))),
        ("2024-W01", ("week", date(2024, 1, 1))),
        ("2024-060", ("ordinal", date(2024, 2, 29))),
        (
            "2024-02-29T23-59-59.999",
            ("datetime", (2024, 2, 29, 23, 59, 59, 999)),
        ),
        ("2024-B6", ("B", (2024, 6))),
        ("2024-Q4", ("Q", (2024, 4))),
        ("2024-T3", ("T", (2024, 3))),
        ("2024-H2", ("H", (2024, 2))),
    ],
)
def test_parse_period_accepts_supported_periods(period, expected):
    assert parse_period(period) == expected


@pytest.mark.parametrize(
    "period",
    [
        "0000",
        "2024-13",
        "2023-02-29",
        "2024-02-30",
        "2024-W00",
        "2024-000",
        "2023-366",
        "2024-02-30T12-00-00.000",
        "2024-02-29T24-00-00.000",
        "2024-B7",
        "2024-Q5",
        "2024-T4",
        "2024-H3",
    ],
)
def test_parse_period_rejects_invalid_periods(period):
    with pytest.raises(ValueError, match=f"Invalid period: {period}"):
        parse_period(period)


@pytest.mark.parametrize(
    ("period", "expected"),
    [
        ("2024", (date(2024, 1, 1), date(2024, 12, 31))),
        ("2024-02", (date(2024, 2, 1), date(2024, 2, 29))),
        ("2023-02", (date(2023, 2, 1), date(2023, 2, 28))),
        ("2024-02-29", (date(2024, 2, 29), date(2024, 2, 29))),
        ("2024-W01", (date(2024, 1, 1), date(2024, 1, 7))),
        ("2024-060", (date(2024, 2, 29), date(2024, 2, 29))),
        (
            "2024-02-29T23-59-59.999",
            (date(2024, 2, 29), date(2024, 2, 29)),
        ),
        ("2024-B6", (date(2024, 11, 1), date(2024, 12, 31))),
        ("2024-Q4", (date(2024, 10, 1), date(2024, 12, 31))),
        ("2024-T3", (date(2024, 9, 1), date(2024, 12, 31))),
        ("2024-H2", (date(2024, 7, 1), date(2024, 12, 31))),
    ],
)
def test_period_date_range_preserves_period_boundaries(period, expected):
    assert period_date_range(period) == expected


@pytest.mark.parametrize("period", ["9999", "9999-12", "9999-W52", "9999-Q4"])
def test_period_date_range_rejects_periods_ending_out_of_range(period):
    with pytest.raises(ValueError, match=f"Invalid period: {period}"):
        period_date_range(period)
