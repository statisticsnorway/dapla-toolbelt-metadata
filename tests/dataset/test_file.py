from dapla_toolbelt_metadata.dataset.first_file import my_name


def test_dataset_folder() -> None:
    name = "Cecilie"
    assert my_name(name) is True
