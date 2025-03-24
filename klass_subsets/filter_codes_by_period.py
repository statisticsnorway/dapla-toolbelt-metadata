from datetime import datetime


def parse_date(date_str: str | None, format: str = "%d.%m.%Y") -> datetime | None:  # noqa: A002
    """Converts date string to datetime object. Returns None for open-ended dates."""
    return datetime.strptime(date_str, format) if date_str else None  # noqa: DTZ007


def filter_codes_by_period(
    codes: list[dict],
    periods: list[dict],
) -> dict[str, list[dict]]:
    """This code places all the subset codes into the correct periods based on the valid from and until.

    Returns:
        A dict the length of the number of periods, where each element in the dict is a list with all the codes for that period.
        This is done like this so that we can create an xml file for each period.
    """
    categorized_codes = [[] for _ in range(len(periods))]

    for code in codes:
        code_valid_from = parse_date(code["valid_from"])
        code_valid_until = parse_date(code["valid_until"]) or datetime.max

        for i, period in enumerate(periods):
            period_from = datetime.strptime(period["valid_from"], "%Y-%m-%d")  # noqa: DTZ007
            period_until = (
                datetime.strptime(period["valid_until"], "%Y-%m-%d")  # noqa: DTZ007
                if period["valid_until"]
                else datetime.max
            )

            # Check if the code is valid in this period
            if code_valid_from < period_until and code_valid_until > period_from:
                categorized_codes[i].append(
                    {
                        "code": code["code"],
                        "nb": code["nb"],
                        "en": code["en"],
                        "nn": code["nn"],
                        "valid_from": code["valid_from"],
                        "valid_until": code["valid_until"],
                        "notes_nb": code["notes_nb"],
                        "notes_en": code["notes_en"],
                        "notes_nn": code["notes_nn"],
                    },
                )

    return categorized_codes


# Example Data
codes = [
    {
        "code": "FGF7",
        "nb": "Test",
        "en": "Test",
        "nn": "Test",
        "valid_from": "01.01.2015",
        "valid_until": "01.01.2018",
        "notes_nb": "Test",
        "notes_en": "Test",
        "notes_nn": "Test",
    },
    {
        "code": "A590",
        "nb": "Avskrivninger",
        "en": "Test",
        "nn": "Test",
        "valid_from": "01.01.2023",
        "valid_until": None,
        "notes_nb": "Test",
        "notes_en": "Test",
        "notes_nn": "Test",
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

    # Print results
    for j, i in enumerate(categorized_codes):
        print(j)  # noqa: T201
        for k in i:
            print(k)  # noqa: T201
