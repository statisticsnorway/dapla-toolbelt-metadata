import requests
from generate_xml import generate_xml
from read_json_codes import find_duplicate_codes
from read_json_codes import read_json_codes

raw_names = [
    "Funksjoner for bydelene i Oslo",
    "Fylkeskommunale funksjoner",
    "Kommunale funksjoner",
    "Detaljerte regnskapstall driftsregnskapet, bydeler i Oslo",
    "Detaljerte regnskapstall driftsregnskapet",
    "Finansielle grunnlagsdata, (fylkes)kommunekasse og konsoliderte regnskap",
    "Finansielle grunnlagsdata, kommunekonsern_",
    "Finansielle grunnlagsdata, fylkeskommunekonsern_",
    "Finansielle nøkkeltall i prosent av brutto driftsinntekter, konsern",
    "Finansielle nøkkeltall i kroner per innbygger, kasse og konsolidert kommune",
    "Finansielle nøkkeltall i kroner per innbygger, kommunekonsern",
    "Finansielle nøkkeltall i kroner per innbygger, fylkeskommunekonsern",
    "Finansiering av driften, kommunekonsern",
    "Finansiering av driften, fylkeskommunekonsern",
    "Finansiering av investeringene, konsern",
    "Hovedtall for drift, investering og finansiering, konsern",
    "Utgifter til tjenesteområdene",
    "Økonomisk oversikt balanse, konsern",
    "Økonomisk oversikt balanse, kasse og konsolidert",
    "Økonomisk oversikt drift, konsern",
    "Økonomisk oversikt drift, kasse og konsolidert",
    "Økonomisk oversikt investering, kasse og konsolidert",
    "Økonomisk oversikt investering, kommunekonsern",
    "Økonomisk oversikt investering, fylkeskommunekonsern",
    "Uttrekk for Kommuner 2020-2023 (uten aggregerte regioner)",
    "Uttrekk for Kommuner 2024- (uten aggregerte regioner)",
    "Uttrekk for Fylkeskommuner 2020-2023 (uten aggregerte regioner)",
    "Uttrekk for Fylkeskommuner 2024- (uten aggregerte regioner)",
    "Uttrekk for Alle fylker 2015-2023",
    "Uttrekk for Alle fylkeskommuner",
    "Uttrekk for Alle kommuner",
    "Uttrekk for Alle fylker",
    "Uttrekk for Fylker 2024-",
    "Uttrekk for Kommuner 2020-2023",
    "Uttrekk for Kommuner -2019",
    "Uttrekk for Fylker 2020-2023",
    "Uttrekk for Kommuner 2024-",
    "Uttrekk for Fylker -2019",
    "Uttrekk for KOSTRA-grupperinger",
    "Uttrekk for Landet",
    "Uttrekk for Fylkeskommuner 2020-2023",
    "Uttrekk for Fylkeskommuner -2019",
    "Uttrekk for Fylkeskommuner 2024-",
    "Uttrekk for KOSTRA-fylkeskommunegrupperinger",
]

# These need suffix in id
add_suffix = [
    "Uttrekk for Alle fylkeskommuner",
    "Uttrekk for Alle kommuner",
    "Uttrekk for Kommuner -2019",
    "Uttrekk for KOSTRA-grupperinger",
    "Uttrekk for Fylker 2020-2023",
    "Uttrekk for Kommuner 2020-2023",
]

special_cases = {
    "Uttrekk for Kommuner -2019": "uttrekk_for_kommuner_-2019_kladd",
    "Uttrekk for Kommuner 2020-2023 (uten aggregerte regioner)": "uttrekk_for_kommuner_2020-2023_uten_aggregerte_regioner",
    "Uttrekk for Fylkeskommuner 2024-": "uttrekk_for_fylkeskommuner_2024-_kladd",
    "Uttrekk for Kommuner 2024-": "uttrekk_for_kommuner_2024-_kladd",
    "Uttrekk for Fylker -2019": "uttrekk_for_fylker_-2019_kladd",
    "Kommunale funksjoner": "uttrekk_for_detaljerte_regnskapstall_driftsregnskapet_kommuner_funksjoner",
    "Uttrekk for Landet": "uttrekk_for_landet_kommuner_kladd",
}


def transform_subset_name(name: str) -> str:
    """Transform name to id."""
    prefix = "uttrekk_for_"
    suffix = "_kladd"
    new_str = name.lower()
    new_str = new_str.replace(" ", "_")
    new_str = new_str.replace(",", "")
    new_str = new_str.replace("(", "")
    new_str = new_str.replace(")", "")
    new_str = new_str.replace("ø", "o")
    new_str = new_str.replace("å", "a")
    if prefix not in new_str:
        new_str = prefix + new_str
    if name in add_suffix:
        new_str = new_str + suffix
    if name in special_cases:
        new_str = special_cases.get(name)
    return new_str


def transform_subset_migrations() -> list:
    """Perform transformations."""
    return_list = []
    for name in raw_names:
        transformed_name = transform_subset_name(name)
        return_list.append(transformed_name)
    return return_list


subsets_migrations = transform_subset_migrations()

bad_request = []
not_found = []
data_list = []
for subset in subsets_migrations:
    result = requests.get(
        f"https://subsets-api.prod-bip-app.ssb.no/v2/subsets/{subset}",
        timeout=5,
    )
    if result.status_code == 400:
        bad_request.append(subset)
    if result.status_code == 404:
        not_found.append(subset)
    else:
        data = result.json()
        data_list.append(data)


### Jørgen sin test kode ###

subset_index = 34
print(subsets_migrations[subset_index])

one_subset = requests.get(
    f"https://subsets-api.prod-bip-app.ssb.no/v2/subsets/{subsets_migrations[subset_index]}",
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
