def read_json_codes(code_file):
    codes = code_file["codes"]

    a = []
    for i in codes:
        # print(
        #     f"Code: {i["code"]}, \n\t nb: {get_language_str("nb",i["name"])}, \n\t nn: {get_language_str("nn",i["name"])}, \n\t en: {get_language_str("en",i["name"])}",
        # )
        # print()

        code = {
            "code": i["code"],
            "nb": get_language_str("nb", i["name"]),
            "nn": get_language_str("nn", i["name"]),
            "en": get_language_str("en", i["name"]),
            "valid_from": i["validFromInRequestedRange"],
            "valid_until": i["validToInRequestedRange"],
        }
        a.append(code)

    return a


def get_language_str(lang_code, name):
    for item in name:
        if item["languageCode"] == lang_code:
            return item["languageText"]
    return "Language not found"


def find_duplicate_codes(code_file):
    list_of_all_codes = []
    codes = code_file["codes"]

    for i in codes:
        list_of_all_codes.append(i["code"])

    from collections import Counter

    counter = Counter(list_of_all_codes)

    for string, count in counter.items():
        if count > 1:
            print(f"'{string}' appears {count} times")
