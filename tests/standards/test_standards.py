import pytest

from dapla_metadata.standards.name_validator import INVALID_SYMBOLS
from dapla_metadata.standards.name_validator import MISSING_DATA_STATE
from dapla_metadata.standards.name_validator import MISSING_DATASET_SHORT_NAME
from dapla_metadata.standards.name_validator import MISSING_PERIOD
from dapla_metadata.standards.name_validator import MISSING_SHORT_NAME
from dapla_metadata.standards.name_validator import NAME_STANDARD_SUCSESS
from dapla_metadata.standards.name_validator import PATH_IGNORED
from dapla_metadata.standards.standard_validators import check_naming_standard


def test_valid_path(setup_test_files):
    test_files, tmp_path = setup_test_files
    for test_file in test_files:
        assert test_file.exists(), f"File {test_file} does not exist."
        assert check_naming_standard(test_file) == NAME_STANDARD_SUCSESS


def test_missing_date_period(setup_test_files_period):
    test_files, tmp_path = setup_test_files_period
    for test_file in test_files:
        assert test_file.exists(), f"File {test_file} does not exist."
        assert check_naming_standard(file_path=test_file) == [MISSING_PERIOD]


def test_missing_data_state(setup_test_files_state):
    test_files, tmp_path = setup_test_files_state
    for test_file in test_files:
        assert test_file.exists(), f"File {test_file} does not exist."
        assert check_naming_standard(file_path=test_file) == MISSING_DATA_STATE


@pytest.mark.parametrize(
    ("file_path"),
    [
        "gs://ssb-staging-dapla-felles-data-delt/inndata/person_data_p2022_v1.parquet",
    ],
)
def test_missing_shortname(file_path, tmp_path):
    test_file = tmp_path / file_path
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.touch()
    assert check_naming_standard(file_path=test_file) == [MISSING_SHORT_NAME]


def test_inored_paths(setup_test_files_ignored):
    test_files, tmp_path = setup_test_files_ignored
    for test_file in test_files:
        assert test_file.exists(), f"File {test_file} does not exist."
        assert check_naming_standard(file_path=test_file) == PATH_IGNORED


def test_invalid_symbols(setup_test_files_invalid_symbols):
    test_files, tmp_path = setup_test_files_invalid_symbols
    for test_file in test_files:
        assert test_file.exists(), f"File {test_file} does not exist."
        assert check_naming_standard(file_path=test_file) == [INVALID_SYMBOLS]


def test_missing_dataset_shortname(setup_test_files_dataset_shortname):
    test_files, tmp_path = setup_test_files_dataset_shortname
    for test_file in test_files:
        assert test_file.exists(), f"File {test_file} does not exist."
        assert check_naming_standard(file_path=test_file) == [
            MISSING_DATASET_SHORT_NAME,
        ]


@pytest.mark.parametrize(
    ("file_path", "violations"),
    [
        (
            "gs://ssb-dapla-example-data-produkt-prod/inndata/skjema_v1.parquet",
            [MISSING_SHORT_NAME, MISSING_PERIOD],
        ),
        (
            "buckets/klargjorte_data/_p2021-12-31_p2021-12-31_v1.parquet",
            [MISSING_SHORT_NAME, MISSING_DATASET_SHORT_NAME],
        ),
        (
            "gs://klargjorte_data/_p2021-12-31_p2021-12-31_v1.parquet",
            [MISSING_SHORT_NAME, MISSING_DATASET_SHORT_NAME],
        ),
    ],
)
def test_missing_multiple(file_path: str, violations: list, tmp_path):
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.touch()
    assert check_naming_standard(file_path=full_path) == violations
