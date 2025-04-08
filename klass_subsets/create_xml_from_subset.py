import requests
from create_all_versions import get_periods
from filter_codes_by_period import filter_codes_by_period
from generate_xml import generate_xml
from no_changes_all_versions import get_all_codes
from transform_data import transform_data

from utils import convert_to_the_nice_structure
from utils import create_subset_dir

mul_ver = []
duplicates = []


def create_xml_file_one_version_from_subset_id(subset_id: str) -> None:
    """Creates an xml file from a subset id. Using all versions of that subset."""
    one_subset = requests.get(
        f"https://subsets-api.prod-bip-app.ssb.no/v2/subsets/{subset_id}",
        timeout=5,
    ).json()

    subset_name = subset_id  # id_to_name(subset_id)

    ### This gets all the codes
    all_codes = get_all_codes(one_subset["versions"])

    subset_dir = create_subset_dir(
        subset_name,
    )

    periods = get_periods(convert_to_the_nice_structure(all_codes))

    transformed_data = transform_data(all_codes["codes"])

    codes = filter_codes_by_period(transformed_data, periods)

    for j, i in enumerate(periods):
        vf = i["valid_from"][:-6]
        vu = None
        if i["valid_until"] is not None:
            vu = i["valid_until"][:-6]

            previous_year = str(int(vu) - 1)
            if vf != vu:
                vu = previous_year
        # print(f"vf: {vf} vu: {vu}")
        codes[j]

        output_file = f"{subset_dir}/{vf}_{vu}_{subset_name}.xml"
        generate_xml(codes[j], output_file)


if __name__ == "__main__":
    with open("resources/subsets_migrations.txt") as f:  # noqa: PTH123
        lines = f.readlines()  # Reads all lines into a list

    lines = [line.strip() for line in lines]

    for i in lines:
        create_xml_file_one_version_from_subset_id(i)
