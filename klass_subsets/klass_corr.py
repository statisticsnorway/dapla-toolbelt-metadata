import requests

BASE_URL = "https://data.ssb.no/api/klass/v1"


def get_changes(classification_id, from_date, to_date):
    url = f"{BASE_URL}/classifications/{classification_id}/changes?from={from_date}&to={to_date}"
    response = requests.get(url, headers={"Accept": "application/json"})

    if response.status_code == 200:
        try:
            data = response.json()
            # print(
            #     "Formatted Response:\n",
            #     json.dumps(data, indent=4, ensure_ascii=False),
            # )
            return data
        except requests.exceptions.JSONDecodeError:
            print("Response is not valid JSON:", response.text)
            return None
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


def remove_code_missing(changes):
    if changes == None:
        return None

    new_codes = {"codeChanges": []}

    for i in changes["codeChanges"]:
        if (i["oldCode"] and i["newCode"] != None) and (i["oldCode"] != i["newCode"]):
            new_codes["codeChanges"].append(i)
    return new_codes


# Classification ID
classification_id = 259
from_date = "2022-01-01"
to_date = "2024-01-01"

# Fetch changes
changes = get_changes(classification_id, from_date, to_date)
