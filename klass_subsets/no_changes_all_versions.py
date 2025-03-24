import requests

from utils import list_duplicates


def get_all_codes(versions: list) -> dict:
    """This is a function that takes all the versions of the subset and returns the lowest valid from date for each code. It also removes duplicates."""
    all_versions_json = []

    # So here we get all versions of a subset and put them all in a list
    for i in versions:
        version_json: dict = requests.get(
            f"https://subsets-api.prod-bip-app.ssb.no/{i}",
            timeout=5,
        ).json()

        all_versions_json.append(version_json)

    all_codes_all_versions = []
    all_versions = []
    all_versions_ending = []
    duplicate_version_no_ending = []
    duplicate_version_ending = []

    for i in all_versions_json:
        duplicates = set(list_duplicates(i))  # Using a set for faster lookups
        for j in i["codes"]:
            code, valid_to = j["code"], j["validToInRequestedRange"]

            all_codes_all_versions.append(code)

            if code in duplicates:
                (
                    duplicate_version_ending
                    if valid_to
                    else duplicate_version_no_ending
                ).append(j)
            else:
                (all_versions_ending if valid_to else all_versions).append(j)

    ##Getting the lowest date for all versions that should always be valid
    all_versions = get_lowest_dates(all_versions)
    duplicate_version_no_ending = get_lowest_dates(duplicate_version_no_ending)

    # Removing duplicates for when we have multiple versions of a subset
    all_versions_ending = remove_duplicate_entries(all_versions_ending)
    duplicate_version_ending = remove_duplicate_entries(duplicate_version_ending)

    duplicates_and_others = (
        all_versions
        + all_versions_ending
        + duplicate_version_no_ending
        + duplicate_version_ending
    )

    a = {}
    a["codes"] = [i for i in duplicates_and_others]  # noqa: C416
    return a


def remove_duplicate_entries(data: list) -> list:
    """This removes duplicate entries form as we wouldn't want to add the same code twice."""
    unique_data = {
        (d["code"], d["validFromInRequestedRange"], d["validToInRequestedRange"]): d
        for d in data
    }
    return list(unique_data.values())


def get_lowest_dates(data: list) -> list:
    """If there is multiple visions of the same code we want to get the one with the lowest valid from date.

    This occurs if a new version of the subset is created and codes have inherited the valid from for just the new version of the subset.
    """
    code_map = {}
    for entry in data:
        code = entry["code"]
        if (
            code not in code_map
            or entry["validFromInRequestedRange"]
            < code_map[code]["validFromInRequestedRange"]
        ):
            code_map[code] = entry
    return list(code_map.values())
