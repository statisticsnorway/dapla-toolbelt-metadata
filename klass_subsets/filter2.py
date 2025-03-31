from datetime import datetime


def parse_date(date_str: str | None, format: str = "%d.%m.%Y") -> datetime | None:
    """Converts date string to datetime object. Returns None for open-ended dates."""
    return datetime.strptime(date_str, format) if date_str else None  # noqa: DTZ007


def is_new_code_present(code, code_to_code):
    return any(entry["newCode"] == code for entry in code_to_code["codeChanges"])


def get_new_code(code, data):
    """Returns the first matching code change entry where oldCode matches the given code."""
    return next((item for item in data["codeChanges"] if item["newCode"] == code), None)


def get_code_change(code, data):
    """Returns the first matching code change entry where oldCode matches the given code."""
    return next((item for item in data["codeChanges"] if item["oldCode"] == code), None)


def is_old_code_present(code, code_to_code):
    if code_to_code is None:
        return None
    return any(entry["oldCode"] == code for entry in code_to_code["codeChanges"])


def get_new_codes_for_old_code(code, code_to_code):
    return [
        entry["newCode"]
        for entry in code_to_code["codeChanges"]
        if entry["oldCode"] == code
    ]


def filter_codes_by_period2(
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


def extract_code_changes(
    categorized_codes: list[dict],
    code_to_code: dict,
) -> list[dict]:
    """Extracts changes per year for each code."""
    changes, previous_codes = [], {}
    starting_period = categorized_codes[0]["valid_from"]

    # Helper function to create a dictionary representing a code change
    def track_changes(previous, current, prev_nb, curr_nb):
        return {
            "previous_code": previous,
            "previous_nb": prev_nb,
            "current_code": current,
            "current_nb": curr_nb,
        }

    # Iterate over each period to detect code changes
    for i, period in enumerate(categorized_codes):
        period_start, current_codes, changes_in_period = period["valid_from"], {}, []

        code_is_added = []
        # Process each code entry in the current period
        for entry in period["codes"]:
            code, current_nb = entry["code"], entry["nb"]
            current_codes[code] = current_nb

            # Check if the code has been replaced with new codes
            if code_to_code is not None:
                old_code_entry = get_code_change(code, code_to_code)
                if old_code_entry and old_code_entry["changeOccurred"] == period_start:
                    for new_code in get_new_codes_for_old_code(code, code_to_code):
                        new_entry = get_new_code(new_code, code_to_code)
                        if new_entry:
                            changes_in_period.append(
                                track_changes(
                                    code,
                                    new_entry["newCode"],
                                    new_entry["oldName"],
                                    new_entry["newName"],
                                ),
                            )
                            code_is_added.append(new_entry["newCode"])

            # Check if the same code has a different name in this period
            if code in previous_codes and previous_codes[code] != current_nb:
                changes_in_period.append(
                    track_changes(code, code, previous_codes[code], current_nb),
                )

            # Check if a new code appears (not seen in previous periods and not a replacement code)
            if (
                code not in previous_codes
                and starting_period != period_start
                and code not in code_is_added
            ):
                changes_in_period.append(track_changes(None, code, None, current_nb))

        # Identify codes that disappear in the next period
        if i < len(categorized_codes) - 1:
            next_codes = {entry["code"] for entry in categorized_codes[i + 1]["codes"]}
            disappearing_codes = [
                code
                for code in current_codes
                if code not in next_codes
                and not is_old_code_present(code, code_to_code)
            ]
            changes_in_period.extend(
                track_changes(code, None, current_codes[code], None)
                for code in disappearing_codes
            )

        # Store detected changes for the period if any exist
        if changes_in_period:
            changes.append({"valid_from": period_start, "codes": changes_in_period})

        # Update previous codes for the next iteration
        previous_codes = current_codes

    return changes


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
        "valid_until": "01.01.2020",
    },
    {
        "code": "FGF7",
        "nb": "Avskrivninger 2",
        "valid_from": "01.01.2020",
        "valid_until": None,
    },
    {
        "code": "A",
        "nb": "Avskrivninger",
        "valid_from": "01.01.2018",
        "valid_until": "01.01.2020",
    },
    {
        "code": "A",
        "nb": "Avskrivninger 2",
        "valid_from": "01.01.2020",
        "valid_until": "01.01.2021",
    },
    {
        "code": "A",
        "nb": "Avskrivninger 3",
        "valid_from": "01.01.2021",
        "valid_until": None,
    },
    {
        "code": "B",
        "nb": "Avskrivninger 3",
        "valid_from": "01.01.2021",
        "valid_until": None,
    },
    {
        "code": "B",
        "nb": "Avskrivninger 3",
        "valid_from": "01.01.2015",
        "valid_until": "01.01.2018",
    },
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
    categorized_codes = filter_codes_by_period2(codes, periods)

    categorized_changes = extract_code_changes(categorized_codes)
    for change in categorized_changes:
        print(change)
