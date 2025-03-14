import requests
from generate_xml import generate_xml
from migration_lists import raw_names
from name_to_id import transform_subset_name_to_id
from read_json_codes import find_duplicate_codes
from read_json_codes import read_json_codes

### Jørgen sin test kode ###


raw_name = raw_names[0]
subset_id = transform_subset_name_to_id(raw_name)

one_subset = requests.get(
    f"https://subsets-api.prod-bip-app.ssb.no/v2/subsets/{subset_id}",
    timeout=5,
).json()


print(one_subset)

import json

with open("parent.json", "w") as file:
    json.dump(one_subset, file, indent=4)  # Saving the parent doc


## Antar vi vil ha en kodeliste per vesjon fra subsets (må kanskje sjekkes ut)
for j, i in enumerate(one_subset["versions"]):
    version_url = i

    # print(version_url)

    # url = "/v2/subsets/uttrekk_for_fylkeskommunale_funksjoner/versions/uttrekk_for_fylkeskommunale_funksjoner_2c5f0adf-0c39-4b9a-8651-700d9ad3c337"

    # one_subset = requests.get(
    #     f"https://subsets-api.prod-bip-app.ssb.no/{url}",
    #     timeout=5,
    # )

    version_json = requests.get(
        f"https://subsets-api.prod-bip-app.ssb.no/{version_url}",
        timeout=5,
    ).json()

    vf = {version_json["validFrom"]}
    vu = None
    try:
        vu = {version_json["validUntil"]}
    except:
        ValueError

    print(
        f"Found subset that is valid from {vf} and valid until {vu} ",
    )

    with open(f"version_{j}_json.json", "w") as file:
        json.dump(version_json, file, indent=4)

    find_duplicate_codes(version_json)
    codes = read_json_codes(version_json)
    output_file = "output.xml"
    generate_xml(codes, output_file)
