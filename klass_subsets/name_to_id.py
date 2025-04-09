from pathlib import Path

from migration_lists import add_suffix
from migration_lists import raw_names
from migration_lists import special_cases


def id_to_name(subset_id: str) -> str:
    """This converts name id to name."""
    for i in raw_names:
        if transform_subset_name_to_id(i) == subset_id:
            return i.replace(" ", "_").replace(",", "")
    print("Not id")
    return None


def transform_subset_name_to_id(name: str) -> str:
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


def write_subset_id_to_file(name_list: list) -> None:
    """Perform transformations."""
    id_list = []
    for name in name_list:
        transformed_name = transform_subset_name_to_id(name)
        id_list.append(transformed_name)
        with Path.open("klass_subsets/resources/subsets_migrations.txt", "w") as f:
            data_to_write = "\n".join(id_list)
            f.write(data_to_write)


# write to file
# write_subset_id_to_file(raw_names)


if __name__ == "__main__":
    with open("resources/subsets_migrations.txt") as f:  # noqa: PTH123
        lines = f.readlines()  # Reads all lines into a list
    lines = [line.strip() for line in lines]

    max_len = max(len(i) for i in lines)

    for i in lines:
        print(f"Id: {i.ljust(max_len)} Name: {id_to_name(i)},")  # noqa: T201
