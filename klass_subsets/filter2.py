from datetime import datetime


def parse_date(date_str: str | None, format: str = "%d.%m.%Y") -> datetime | None:
    """Converts date string to datetime object. Returns None for open-ended dates."""
    return datetime.strptime(date_str, format) if date_str else None  # noqa: DTZ007


def filter_codes_by_period(
    codes: list[dict],
    periods: list[dict],
) -> list[dict]:
    """Categorizes codes into periods based on validity dates."""
    categorized_periods = []

    for period in periods:
        period_from = datetime.strptime(period["valid_from"], "%Y-%m-%d")  # noqa: DTZ007
        period_until = (
            datetime.strptime(period["valid_until"], "%Y-%m-%d")  # noqa: DTZ007
            if period["valid_until"]
            else datetime.max
        )

        period_codes = []
        for code in codes:
            code_valid_from = parse_date(code["valid_from"])
            code_valid_until = parse_date(code["valid_until"]) or datetime.max

            if code_valid_from < period_until and code_valid_until > period_from:
                period_codes.append(
                    {
                        "code": code["code"],
                        "nb": code["nb"],
                        "valid_from": code["valid_from"],
                        "valid_until": code["valid_until"],
                    },
                )

        categorized_periods.append(
            {
                "valid_from": period["valid_from"],
                "valid_until": period["valid_until"],
                "codes": period_codes,
            },
        )

    return categorized_periods


def find_changes(data):
    previous_nb = None

    for entry in data:
        current_nb = entry["codes"][0]["nb"]  # Assuming only one code per entry
        if previous_nb is not None and current_nb != previous_nb:
            print(
                f"Change detected! '{previous_nb}' -> '{current_nb}' (from {entry['valid_from']})",
            )
        previous_nb = current_nb


# Example Data
codes = [
    {
        "code": "FGF7",
        "nb": "Test",
        "valid_from": "01.01.2015",
        "valid_until": "01.01.2018",
    },
    {
        "code": "FGF7",
        "nb": "Avskrivninger",
        "valid_from": "01.01.2018",
        "valid_until": None,
    },  # Still valid
]

periods = [
    {"valid_from": "2015-01-01", "valid_until": "2018-01-01"},
    {"valid_from": "2018-01-01", "valid_until": "2020-01-01"},
    {"valid_from": "2020-01-01", "valid_until": "2021-01-01"},
    {"valid_from": "2021-01-01", "valid_until": "2023-01-01"},
    {"valid_from": "2023-01-01", "valid_until": None},  # Open-ended period
]


if __name__ == "__main__":
    # Run function
    categorized_codes = filter_codes_by_period(codes, periods)

    find_changes(categorized_codes)

    # for j, i in enumerate(categorized_codes):
    #    print(f"{i['valid_from']} -> {i['valid_until']}: {i['codes']}")
