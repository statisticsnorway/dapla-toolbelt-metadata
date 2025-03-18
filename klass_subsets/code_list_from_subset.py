import requests
from generate_xml import generate_xml
from read_json_codes import create_subset_dir
from read_json_codes import find_duplicate_codes
from read_json_codes import get_validity_periods
from read_json_codes import read_json_codes

### Jørgen sin test kode ###


def create_xml_file_from_subset_id(subset_id: str) -> None:  # noqa: D103
    print("Generating file for subset with id: ", subset_id)  # noqa: T201

    one_subset = requests.get(
        f"https://subsets-api.prod-bip-app.ssb.no/v2/subsets/{subset_id}",
        timeout=5,
    ).json()

    ## Antar vi vil ha en kodeliste per vesjon fra subsets (må kanskje sjekkes ut)
    for j, i in enumerate(one_subset["versions"]):
        version_json: dict = requests.get(
            f"https://subsets-api.prod-bip-app.ssb.no/{i}",
            timeout=5,
        ).json()

        vf, vu = get_validity_periods(version_json)

        codes = read_json_codes(version_json)

        subset_dir = create_subset_dir(
            subset_id,
        )  # So we want to create one dir per subset for now so it's no hard to find stuff
        output_file = f"{subset_dir}/{subset_id}_{vf}.xml"

        generate_xml(codes, output_file)

        find_duplicate_codes(
            version_json,
            subset_id=subset_id,
            version=vf,
            path=subset_dir,
        )


if __name__ == "__main__":
    with open("resources/subsets_migrations.txt") as f:  # noqa: PTH123
        lines = f.readlines()  # Reads all lines into a list

    lines = [line.strip() for line in lines]

    for i in lines:
        create_xml_file_from_subset_id(i)
