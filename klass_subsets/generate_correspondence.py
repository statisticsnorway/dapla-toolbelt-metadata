import json

import requests
from correspondence_xml import generate_correspondence_xml
from create_all_versions import get_periods
from filter2 import extract_code_changes
from filter2 import filter_codes_by_period2
from filter_codes_by_period import filter_codes_by_period
from klass_corr import get_changes
from klass_corr import remove_code_missing
from no_changes_all_versions import get_all_codes
from transform_data import transform_data

from utils import convert_to_the_nice_structure
from utils import create_subset_dir
from utils import find_duplicate_new_codes


def correspondences(subset_id: str) -> None:
    """Creates an xml file from a subset id. Using all versions of that subset."""
    one_subset = requests.get(
        f"https://subsets-api.prod-bip-app.ssb.no/v2/subsets/{subset_id}",
        timeout=5,
    ).json()

    ### This gets all the codes
    all_codes = get_all_codes(one_subset["versions"])

    subset_dir = create_subset_dir(
        subset_id,
    )

    periods = get_periods(convert_to_the_nice_structure(all_codes))

    print("ID: ", subset_id)
    classification_id = str(all_codes["codes"][0]["classificationId"])
    changes = get_changes(classification_id, periods[0]["valid_from"], "2025-01-01")
    if changes is not None:
        changes = remove_code_missing(changes)
        find_duplicate_new_codes(changes)

    with open("b.json", "w") as f:
        json.dump(changes, f, indent=2)

    transformed_data = transform_data(all_codes["codes"])

    filter_codes_by_period(transformed_data, periods)

    categorized_codes = filter_codes_by_period2(transformed_data, periods)
    categorized_changes = extract_code_changes(categorized_codes, changes)

    for change in categorized_changes:
        vf = change["valid_from"]

        output_file = f"{subset_dir}/{vf}_{subset_id}_correspondences.xml"
        generate_correspondence_xml(change["codes"], output_file)
    print()


if __name__ == "__main__":
    with open("resources/subsets_migrations.txt") as f:  # noqa: PTH123
        lines = f.readlines()  # Reads all lines into a list

    lines = [line.strip() for line in lines]

    for i in lines:
        correspondences(i)
