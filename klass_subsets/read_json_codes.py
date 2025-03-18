from collections import Counter
from datetime import datetime
from pathlib import Path


def read_json_codes(code_file: dict) -> list[dict]:
    """Reads all codes from a subset file."""
    codes = code_file["codes"]

    list_of_codes = []
    for i in codes:
        code = {
            "code": i["code"],
            "nb": get_language_str("nb", i["name"]),
            "nn": get_language_str("nn", i["name"]),
            "en": get_language_str("en", i["name"]),
            "valid_from": convert_dates(i["validFromInRequestedRange"]),
            "valid_until": convert_dates(i["validToInRequestedRange"]),
        }
        list_of_codes.append(code)

    return list_of_codes


def convert_dates(date: str) -> str:  # noqa: D103
    try:
        return datetime.strptime(date, "%Y-%m-%d").strftime("%d.%m.%Y")  # noqa: DTZ007
    except:  # noqa: E722
        ValueError  # noqa: B018


def get_language_str(lang_code: str, name: str) -> str:
    """Gives us the requested language."""
    for item in name:
        if item["languageCode"] == lang_code:
            return item["languageText"]
    return "Language not found"


def find_duplicate_codes(
    code_file: dict,
    subset_id: str,
    version: str,
    path: str,
) -> None:
    """Finds duplicate codes in the subset file."""
    codes = code_file["codes"]

    list_of_all_codes = [i["code"] for i in codes]

    counter = Counter(list_of_all_codes)

    duplicates = []
    for string, count in counter.items():
        if count > 1:
            duplicates.append(string)
            print(f"'{string}' appears {count} times")  # noqa: T201

    if len(duplicates) > 0:
        with open(f"{path}/{subset_id}_duplicates_version_{version}.txt", "w") as f:  # noqa: PTH123
            for i in duplicates:
                f.write(f"{i}\n")


def create_subset_dir(subset_id: str) -> str:  # noqa: D103
    parent_folder = Path("converted_subsets")
    new_directory = parent_folder / subset_id
    new_directory.mkdir(parents=True, exist_ok=True)
    return str(new_directory)


def get_validity_periods(version_json: dict):  # noqa: ANN201, D103
    vf = version_json["validFrom"]
    vu = None
    try:
        vu = version_json["validUntil"]
    except:  # noqa: E722
        ValueError  # noqa: B018
    print(  # noqa: T201
        f"Found subset that is valid from {vf} and valid until {vu} ",
    )
    return vf, vu
