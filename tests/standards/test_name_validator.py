import os

import pytest

from dapla_metadata.standards.name_validator import MISSING_DATASET_SHORT_NAME
from dapla_metadata.standards.name_validator import NAME_STANDARD_SUCSESS
from dapla_metadata.standards.name_validator import NameStandardValidator


@pytest.mark.parametrize(
    ("data", "expected_result"),
    [
        (
            "buckets/ssb-dapla-example-data-produkt-prod/ledstill/utdata/persån_testdata_p2021-12-31_p2021-12-31_v1.parquet",
            True,
        ),
        (
            "buckets/ssb-dapla-example-data-produkt-prod/ledstill/utdata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
            False,
        ),
        (
            "ssb-dapla-example-data-produkt-prod/ledstill/oppdrag/skjema_p2018_p2020_v1",
            False,
        ),
        (
            "ssbÆ-dapla-example-data-produkt-prod/ledstill/oppdrag/skjema_p2018_p2020_v1",
            True,
        ),
    ],
)
def test_symbols_in_filepath(data: str, expected_result: bool):
    assert NameStandardValidator.is_invalid_symbols(data) == expected_result


def test_validate_directory():
    """Test recursive directory validation."""
    os.chdir("tests/standards/resources/buckets")
    validator = NameStandardValidator(
        file_path=None,
        bucket_name="produkt",
    )
    results = validator.validate_bucket()
    assert results[0][1] == NAME_STANDARD_SUCSESS


def test_validate_directory_2():
    os.chdir("tests/standards")
    validator = NameStandardValidator(
        file_path="./resources/buckets/produkt/stat/inndata/person_data_p2021_v2.parquet",
        bucket_name=None,
    )
    results = validator.validate()
    assert results == NAME_STANDARD_SUCSESS


def test_validate_directory_3():
    os.chdir("tests/")
    validator = NameStandardValidator(
        file_path="./standards/resources/buckets/produkt/stat/inndata/p2021_v2.parquet",
        bucket_name=None,
    )
    results = validator.validate()
    assert results == [MISSING_DATASET_SHORT_NAME]
