import datetime
from pathlib import Path

import pytest

from dapla_metadata.dapla.name_validator import INVALID_SYMBOLS
from dapla_metadata.dapla.name_validator import MISSING_DATA_STATE
from dapla_metadata.dapla.name_validator import MISSING_PERIOD
from dapla_metadata.dapla.name_validator import MISSING_SHORT_NAME
from dapla_metadata.dapla.name_validator import NAME_STANDARD_SUCSESS
from dapla_metadata.dapla.name_validator import PATH_IGNORED
from dapla_metadata.dapla.name_validator import NameStandardValidator
from dapla_metadata.dapla.name_validator import _is_invalid_symbols
from dapla_metadata.dapla.standards import check_naming_standard
from dapla_metadata.datasets.dapla_dataset_path_info import DaplaDatasetPathInfo


@pytest.mark.parametrize(
    ("data"),
    [
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/utdata/person_data_p2021_v2.parquet",
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/utdata/person_data_p2021_p2022_v2.parquet",
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/utdata/undermappe/person_data_p2021_v2.parquet",
        "buckets/dataset/klargjorte_data/arbmark/resources/person_data_p2021-12-31_p2021-12-31_v1.parquet",
        "buckets/inndata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "buckets/klargjorte-data/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "buckets/utdata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "buckets/utdata/person_testdata_p2021-12-31_p2021-12-31_v1",
        "buckets/utdata/dapla/person_testdata_p2021-12-31_p2021-12-31_v1",
        "ssb-dapla-example-data-produkt-prod/ledstill/inndata/skjema_p2018_p2020_v1",
        "/buckets/produkt/datadoc/brukertest/1/sykefratot/klargjorte_data/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "buckets/produkt/datadoc/brukertest/1/sykefratot/klargjorte_data/person_testdata_p2021-12-31_p2021-12-31_v1.json",
    ],
)
def test_valid_names(data: str):
    assert check_naming_standard(data) == NAME_STANDARD_SUCSESS


@pytest.mark.parametrize(
    ("data"),
    [
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/utdata/person_data_v1.parquet",
        "tests/dataset/klargjorte_data/arbmark/resources/person_data_v1.parquet",
    ],
)
def test_missing_date_period(data: str):
    assert check_naming_standard(data) == [MISSING_PERIOD]


@pytest.mark.parametrize(
    ("data"),
    [
        "gs://ssb-staging-dapla-felles-data-delt/stat_reg/person_data_p2022_v1.parquet",
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/person_data_p2021_v3.parquet",
        "buckets/produkt/test-2/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
    ],
)
def test_missing_required_data_state_folder(data: str):
    assert check_naming_standard(data) == [MISSING_DATA_STATE, MISSING_SHORT_NAME]


@pytest.mark.parametrize(
    ("data"),
    [
        "gs://ssb-staging-dapla-felles-data-delt/inndata/person_data_p2022_v1.parquet",
        "gs://ssb-staging-dapla-felles-data-delt/klargjorte-data/person_data_p2021_v3.parquet",
        "buckets/produkt/utdata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
    ],
)
def test_missing_shortname_folder(data: str):
    assert check_naming_standard(data) == NAME_STANDARD_SUCSESS


@pytest.mark.parametrize(
    ("data"),
    [
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/person_data_v1.parquet",
    ],
)
def test_invalid_date_and_dir(data: str):
    assert check_naming_standard(data) == [
        MISSING_DATA_STATE,
        MISSING_SHORT_NAME,
        MISSING_PERIOD,
    ]


@pytest.mark.parametrize(
    ("data"),
    [
        "ssb-dapla-example-data-produkt-prod/oppdrag/ledstill/skjema_p2018_p2020_v1",
    ],
)
def test_names_oppdrag_dir(data: str):
    assert check_naming_standard(data) == [
        MISSING_DATA_STATE,
        MISSING_SHORT_NAME,
    ]


@pytest.mark.parametrize(
    ("data"),
    [
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/temp/skjema_v1.parquet",
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/inndata/temp/skjema_p2018_p2020_v2.parquet",
        "gs://ssb-dapla-example-data-produkt-prod/temp/ledstill/inndata/temp/skjema_p2018_p2020",
    ],
)
def test_temp_dir(data: str):
    assert check_naming_standard(data) == PATH_IGNORED


@pytest.mark.parametrize(
    ("data"),
    [
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/kildedata/skjema_v1",
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/kildedata/skjema_p2018_p2020_v1",
        "gs://ssb-dapla-example-data-produkt-prod/ledstill/kildedata/skjema_p2018_p2020_v1",
    ],
)
def test_source_data_is_ignored(data: str):
    assert check_naming_standard(data) == PATH_IGNORED


@pytest.mark.parametrize(
    ("data"),
    [
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/utdata/persån_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "gs://ssb-dapla-example-data-prædukt-prod/ledstill/utdata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
    ],
)
def test_invalid_symbols(data: str):
    assert check_naming_standard(data) == [INVALID_SYMBOLS]


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
    assert _is_invalid_symbols(data) == expected_result


@pytest.mark.parametrize(
    ("data", "expected_result"),
    [
        (
            "buckets/ssb-dapla-example-data-produkt-prod/ledstill/utdata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
            False,
        ),
        (
            "buckets/ssb-dapla-example-data-produkt-prod",
            True,
        ),
        (
            "buckets/ssb-dapla-example-data-produkt-prod/",
            True,
        ),
        (
            "ssb-dapla-example-data-produkt-prod/ledstill/oppdrag/skjema_p2018_p2020_v1",
            False,
        ),
        (
            "gs://bucket-name",
            True,
        ),
        (
            "gs://bucket-name/",
            True,
        ),
    ],
)
def test_is_bucket_name(data, expected_result):
    file = NameStandardValidator(data)
    assert file.is_bucket == expected_result


def test_validate_bucket():
    buckets_dir = Path("buckets")
    buckets_dir.mkdir(parents=True, exist_ok=True)
    buckets_name = buckets_dir / "bucket_name"
    buckets_name.mkdir(parents=True, exist_ok=True)
    file = NameStandardValidator("buckets/bucket_name")
    result = file.validate
    assert result == "Something"


def test_validate_bucket_2():
    file = NameStandardValidator("buckets/hoover")
    with pytest.raises(NotADirectoryError):
        file.validate()


def test_bucket_name_is_directory():
    buckets_dir = Path("buckets")
    buckets_dir.mkdir(parents=True, exist_ok=True)
    assert buckets_dir.is_dir()
    buckets_name = buckets_dir / "bucket_name"
    buckets_name.mkdir(parents=True, exist_ok=True)
    assert buckets_name.is_dir()
    file = NameStandardValidator(str(buckets_name))
    assert file.bucket_name == "bucket_name"


def test_dapla_invalid_characters():
    dataset_path = DaplaDatasetPathInfo(
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/utdata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
    )
    assert dataset_path.bucket_name == "ssb-dapla-example-data-produkt-prod"
    assert dataset_path.statistic_short_name == "ledstill"
    assert dataset_path.dataset_state == "OUTPUT_DATA"
    assert dataset_path.path_complies_with_naming_standard() is True


def test_dapla_dataset_path_source_data():
    dataset_path = DaplaDatasetPathInfo(
        "gs://dataset/kildedata/arbmark/resources/person_data_p2021-12-31_p2021-12-31_v1.parquet",
    )
    assert dataset_path.bucket_name == "dataset"
    assert dataset_path.statistic_short_name == "dataset"
    assert dataset_path.dataset_state == "SOURCE_DATA"
    assert dataset_path.path_complies_with_naming_standard() is True


def test_dapla_dataset_path():
    dataset_path = DaplaDatasetPathInfo(
        "buckets/dataset/klargjorte_data/arbmark/resources/person_data_p2021-12-31_p2021-12-31_v1.parquet",
    )
    assert dataset_path.contains_data_from == datetime.date(2021, 12, 31)
    assert dataset_path.path_complies_with_naming_standard() is True


def test_dapla_dataset_path_not():
    dataset_path = DaplaDatasetPathInfo(
        "tests/dataset/klargjorte_data/arbmark/resources/person_data_v1.parquet",
    )
    assert dataset_path.path_complies_with_naming_standard() is False
