from datetime import datetime
from typing import Any


def parse_date(date_str: str) -> datetime:  # noqa: D103
    return datetime.strptime(date_str, "%Y-%m-%d")  # noqa: DTZ007


def get_periods(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Extract unique date ranges from data to determine what XML document versions we want."""
    dates = {parse_date(item["valid_from"]) for item in data}
    dates |= {
        parse_date(item["valid_until"]) for item in data if item["valid_until"]
    }  # Union update

    sorted_dates = sorted(dates)
    periods = [
        {
            "valid_from": d.strftime("%Y-%m-%d"),
            "valid_until": sorted_dates[i + 1].strftime("%Y-%m-%d"),
        }
        for i, d in enumerate(sorted_dates[:-1])
    ]

    if any(item.get("valid_until") is None for item in data):
        periods.append(
            {"valid_from": sorted_dates[-1].strftime("%Y-%m-%d"), "valid_until": None},
        )

    return periods


if __name__ == "__main__":
    sample_data = [
        {"code": "465", "valid_from": "2015-01-01", "valid_until": "2020-01-01"},
        {"code": "465", "valid_from": "2023-01-01", "valid_until": None},
        {"code": "FGF7", "valid_from": "2015-01-01", "valid_until": "2018-01-01"},
        {"code": "FGF7", "valid_from": "2023-01-01", "valid_until": None},
        {"code": "455", "valid_from": "2015-01-01", "valid_until": "2023-01-01"},
        {"code": "455", "valid_from": "2023-01-01", "valid_until": None},
        {"code": "456", "valid_from": "2015-01-01", "valid_until": "2016-01-01"},
        {"code": "456", "valid_from": "2022-01-01", "valid_until": None},
    ]

    consolidated_ranges = get_periods(sample_data)

    print("Consolidated Date Ranges:")  # noqa: T201
    for i, range_item in enumerate(consolidated_ranges, 1):
        valid_until = (
            range_item["valid_until"] if range_item["valid_until"] else "onwards"
        )
        print(f"Range {i}: {range_item['valid_from']} to {valid_until}")  # noqa: T201
