import requests
from create_all_versions import get_periods
from filter_codes_by_period import filter_codes_by_period
from no_changes_all_versions import get_all_codes
from transform_data import transform_data

from utils import convert_to_the_nice_structure
from utils import create_subset_dir


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

    transformed_data = transform_data(all_codes["codes"])

    codes = filter_codes_by_period(transformed_data, periods)

    for j, i in enumerate(periods):
        vf = i["valid_from"]
        vu = i["valid_until"]
        codes[j]

        print()

    #     output_file = f"{subset_dir}/{subset_id}_{vf}_{vu}.xml"
    #     generate_xml(codes[j], output_file)





def find_changes():
    







if __name__ == "__main__":
    with open("resources/subsets_migrations.txt") as f:  # noqa: PTH123
        lines = f.readlines()  # Reads all lines into a list

    lines = [line.strip() for line in lines]

    for i in lines:
        correspondences(i)


