from datetime import datetime


def transform_data(data_list: list) -> list:
    """This transforms the data into a format that is easier to work with and has only the fields we want to use."""
    transformed_list = []

    for item in data_list:
        transformed_item = {
            "code": item["code"],
            "valid_from": datetime.strptime(  # noqa: DTZ007
                item["validFromInRequestedRange"],
                "%Y-%m-%d",
            ).strftime("%d.%m.%Y")
            if item["validFromInRequestedRange"]
            else None,
            "valid_until": datetime.strptime(  # noqa: DTZ007
                item["validToInRequestedRange"],
                "%Y-%m-%d",
            ).strftime("%d.%m.%Y")
            if item["validToInRequestedRange"]
            else None,
        }

        # Extract names
        for name in item["name"]:
            transformed_item[name["languageCode"]] = name["languageText"]
        # Extract notes
        for note in item["notes"]:
            transformed_item[f"notes_{note['languageCode']}"] = (
                note["languageText"] if note["languageText"] else None
            )

        transformed_list.append(transformed_item)

    return transformed_list


# Example usage:
data = [
    {
        "code": "AGB5",
        "name": [
            {
                "languageCode": "nb",
                "languageText": "Korrigerte brutto driftsutgifter p\u00e5 funksjon/tjenesteomr\u00e5de, bydel",
            },
            {
                "languageCode": "nn",
                "languageText": "Korrigerte brutto driftsutgifter p\u00e5 funksjon/tenesteomr\u00e5de, bydel",
            },
            {
                "languageCode": "en",
                "languageText": "Adjusted gross operating expenditure, districts of Oslo",
            },
        ],
        "rank": 1,
        "level": "1",
        "notes": [
            {
                "languageCode": "nb",
                "languageText": "Korrigerte brutto driftsutgifter kan si noe om hva det koster...",
            },
            {"languageCode": "nn", "languageText": ""},
            {"languageCode": "en", "languageText": ""},
        ],
        "classificationId": "259",
        "classificationVersions": [
            "https://data.ssb.no/api/klass/v1/versions/795",
            "https://data.ssb.no/api/klass/v1/versions/812",
        ],
        "validToInRequestedRange": None,
        "validFromInRequestedRange": "2015-01-01",
    },
    {
        "code": "AGB5",
        "name": [
            {
                "languageCode": "nb",
                "languageText": "l",
            },
            {
                "languageCode": "nn",
                "languageText": "Korrigerte brutto driftsutgifter p\u00e5 funksjon/tenesteomr\u00e5de, bydel",
            },
            {
                "languageCode": "en",
                "languageText": "Adjusted gross operating expenditure, districts of Oslo",
            },
        ],
        "rank": 1,
        "level": "1",
        "notes": [
            {
                "languageCode": "nb",
                "languageText": "Korrigerte brutto driftsutgifter kan si noe om hva det koster...",
            },
            {"languageCode": "nn", "languageText": ""},
            {"languageCode": "en", "languageText": ""},
        ],
        "classificationId": "259",
        "classificationVersions": [
            "https://data.ssb.no/api/klass/v1/versions/795",
            "https://data.ssb.no/api/klass/v1/versions/812",
        ],
        "validToInRequestedRange": None,
        "validFromInRequestedRange": "2015-01-01",
    },
]

if __name__ == "__main__":
    transformed_data = transform_data(data)
    print(transformed_data)
