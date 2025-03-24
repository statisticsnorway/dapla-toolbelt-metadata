from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


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


def create_subset_dir(subset_id: str) -> str:
    """This creates the directory for the generated files."""
    parent_folder = Path("converted_subsets")
    new_directory = parent_folder / subset_id
    new_directory.mkdir(parents=True, exist_ok=True)
    return str(new_directory)


def list_duplicates(code_file: dict) -> list:  # noqa: D103
    counter = Counter(i["code"] for i in code_file["codes"])
    return [code for code, count in counter.items() if count > 1]


def convert_to_the_nice_structure(
    code_file: dict,
) -> list[dict[str, Any]] | None:
    """This converts the codes to a format that is easier to work with."""
    codes = code_file["codes"]

    # Find all duplicates
    return [
        {
            "code": i["code"],
            "valid_from": i["validFromInRequestedRange"],
            "valid_until": i["validToInRequestedRange"],
        }
        for i in codes
    ]
