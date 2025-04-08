import json
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


def extract_code_changes_2(
    categorized_codes: list[dict],
    code_to_code,
) -> list[dict]:
    changes = []

    if code_to_code != None:
        code_to_code = code_to_code["codeChanges"]

    previous_codes = None
    for i, period in enumerate(categorized_codes):
        period_start = period["valid_from"]
        period_end = period["valid_until"]

        this_period_codes = period["codes"]

        # print(f"Start: {period_start}, end: {period_end}")

        if i > 0:
            changes_in_period = find_changes(
                previous_codes,
                this_period_codes,
                code_to_code,
                period_start,
            )

            disappearing_codes = code_disappears(
                previous_codes,
                this_period_codes,
            )

            for i in disappearing_codes:
                is_not_in_previous = all(
                    entry["previous_code"] != i["code"] for entry in changes_in_period
                )
                if is_not_in_previous:
                    changes_in_period.append(
                        {
                            "previous_code": i["code"],
                            "previous_nb": i["nb"],
                            "current_code": None,
                            "current_nb": None,
                        },
                    )

            changes.append({"valid_from": period_start, "codes": changes_in_period})

        previous_codes = period["codes"]
    return changes


def find_changes(previous_codes, this_period_codes, code_to_code, period_start):
    changes_in_period = []

    def track_changes(previous_code, prev_nb, current_code, curr_nb):
        return {
            "previous_code": previous_code,
            "previous_nb": prev_nb,
            "current_code": current_code,
            "current_nb": curr_nb,
        }

    for i in this_period_codes:
        name_changed = code_changed_but_not_name(
            previous_codes,
            i["nb"],
            i["code"],
        )

        code_changed = name_changed_but_not_code(
            previous_codes,
            i["nb"],
            i["code"],
        )

        if code_to_code:
            code_combined_to_new_code = code_combined_to_new(
                i["code"],
                code_to_code,
                period_start,
            )
        else:
            code_combined_to_new_code = False
        if code_to_code:
            code_split_to_mul_codes = code_split_to_new_codes(
                i["code"],
                code_to_code,
                period_start,
            )
        else:
            code_split_to_mul_codes = False

        new_code_appears = code_appears(
            previous_codes,
            i["code"],
        )

        if name_changed:
            changes_in_period.append(
                track_changes(
                    get_code_changed_but_not_name(previous_codes, i["nb"], i["code"]),
                    i["nb"],
                    i["code"],
                    i["nb"],
                ),
            )
        elif code_changed:
            changes_in_period.append(
                track_changes(
                    i["code"],
                    get_name_changed_but_not_code(previous_codes, i["nb"], i["code"]),
                    i["code"],
                    i["nb"],
                ),
            )
        elif code_combined_to_new_code:
            if code_to_code:
                for j in get_all_code_combined_to_new(
                    i["code"],
                    code_to_code,
                    period_start,
                ):
                    changes_in_period.append(  # noqa: PERF401
                        track_changes(j["code"], j["name"], i["code"], i["nb"]),
                    )
        elif code_split_to_mul_codes:
            if code_to_code:
                split = get_split_name_code(
                    i["code"],
                    code_to_code,
                    period_start,
                )

                changes_in_period.append(
                    track_changes(
                        split["code"],
                        split["name"],
                        i["code"],
                        i["nb"],
                    ),
                )
        elif new_code_appears:
            changes_in_period.append(
                track_changes(
                    None,
                    None,
                    i["code"],
                    i["nb"],
                ),
            )

    return changes_in_period


# This checks
def code_changed_but_not_name(previous_codes, name, code):
    return any(i["nb"] == name and i["code"] != code for i in previous_codes)


# This gets
def get_code_changed_but_not_name(previous_codes, name, code):
    for i in previous_codes:
        if i["nb"] == name and i["code"] != code:
            return i["code"]
    return None


def name_changed_but_not_code(previous_codes, name, code):
    return any(i["nb"] != name and i["code"] == code for i in previous_codes)


def get_name_changed_but_not_code(previous_codes, name, code):
    for i in previous_codes:
        if i["nb"] != name and i["code"] == code:
            return i["nb"]
    return None


def code_split_to_new_codes(new_code, code_to_code, period_start):
    for i in code_to_code:
        if i["changeOccurred"] == period_start and new_code == i["newCode"]:
            return True
    return False


def get_split_name_code(new_code, code_to_code, period_start):
    for i in code_to_code:
        if i["changeOccurred"] == period_start and new_code == i["newCode"]:
            return {"code": i["oldCode"], "name": i["oldName"]}
    return None


def code_combined_to_new(new_code, code_to_code, period_start):
    old_codes = []
    for i in code_to_code:
        if i["changeOccurred"] == period_start and new_code == i["newCode"]:
            old_codes.append(i["oldCode"])

    return len(old_codes) > 1


def get_all_code_combined_to_new(new_code, code_to_code, period_start):
    old_codes = []
    for i in code_to_code:
        if i["changeOccurred"] == period_start and new_code == i["newCode"]:
            old_codes.append({"code": i["oldCode"], "name": i["oldName"]})

    return old_codes


# def mul_code_into_new_code(new_code, code_to_code):
#     list_of_codes = []
#     for i in code_to_code:
#         if i["newCode"] == new_code:
#             list_of_codes.append(i["oldCode"])
#     if len(list_of_codes) > 1:
#         print(list_of_codes)

#     return len(list_of_codes) > 1


# def code_split_to_new_codes(new_code, code_to_code):
#     list_of_codes = []
#     for i in code_to_code:
#         if i["newCode"] == new_code:
#             list_of_codes.append(i["oldCode"])

#     # if new_code == "A871":
#     #    print(list_of_codes)
#     return len(list_of_codes) > 1


def code_appears(previous_codes, code):
    return not any(code in i["code"] for i in previous_codes)


# Adding all current codes that disappear
def code_disappears(previous_codes, current_codes):
    current_code_values = [i["code"] for i in current_codes]

    disappearing_codes = []
    for i in previous_codes:
        if i["code"] not in current_code_values:
            disappearing_codes.append(i)  # noqa: PERF401
    return disappearing_codes


if __name__ == "__main__":
    with open("periods_to_test_c2c.json") as json_data:
        json_codes = json.load(json_data)

    with open("code_to_code.json") as json_data:
        code_to_code = json.load(json_data)

    # with open("periods_to_test.json") as json_data:
    #    json_codes = json.load(json_data)

    categorized_changes = extract_code_changes_2(json_codes, code_to_code)
    # for change in categorized_changes:
    #     print(change)
