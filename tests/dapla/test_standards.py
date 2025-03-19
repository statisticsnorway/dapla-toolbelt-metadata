import datetime

import pytest

from dapla_metadata.dapla.name_validator import MISSING_DATA_STATE
from dapla_metadata.dapla.name_validator import MISSING_PERIOD
from dapla_metadata.dapla.name_validator import MISSING_SHORT_NAME
from dapla_metadata.dapla.name_validator import NAME_STANDARD_SUCSESS
from dapla_metadata.dapla.name_validator import PATH_IGNORED
from dapla_metadata.dapla.standards import check_naming_standard
from dapla_metadata.datasets.dapla_dataset_path_info import DaplaDatasetPathInfo


def test_file_path_does_not_follow_naming_standard():
    assert check_naming_standard(
        "tests/dataset/klargjorte_data/arbmark/resources/person_data_v1.parquet",
    ) == [MISSING_PERIOD]


def test_file_path_follow_naming_standard():
    assert (
        check_naming_standard(
            "buckets/dataset/klargjorte_data/arbmark/resources/person_data_p2021-12-31_p2021-12-31_v1.parquet",
        )
        == NAME_STANDARD_SUCSESS
    )


def test_dapla_dataset_path():
    dataset_path = DaplaDatasetPathInfo(
        "buckets/dataset/klargjorte_data/arbmark/resources/person_data_p2021-12-31_p2021-12-31_v1.parquet",
    )
    assert dataset_path.bucket_name is None
    assert dataset_path.contains_data_from == datetime.date(2021, 12, 31)
    assert dataset_path.path_complies_with_naming_standard() is True


def test_dapla_invalid_characters():
    dataset_path = DaplaDatasetPathInfo(
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/utdata/persån_testdata_p2021-12-31_p2021-12-31_v1.parquet",
    )
    assert dataset_path.bucket_name is None
    assert dataset_path.contains_data_from == datetime.date(2021, 12, 31)
    assert dataset_path.path_complies_with_naming_standard() is True


def test_dapla_dataset_path_source_data():
    dataset_path = DaplaDatasetPathInfo(
        "buckets/dataset/kildedata/arbmark/resources/person_data_p2021-12-31_p2021-12-31_v1.parquet",
    )
    assert dataset_path.bucket_name is None
    assert dataset_path.dataset_state == "SOURCE_DATA"
    assert dataset_path.path_complies_with_naming_standard() is True


def test_dapla_dataset_path_not():
    dataset_path = DaplaDatasetPathInfo(
        "tests/dataset/klargjorte_data/arbmark/resources/person_data_v1.parquet",
    )
    assert dataset_path.path_complies_with_naming_standard() is False


@pytest.mark.parametrize(
    ("data"),
    [
        "gs://ssb-staging-dapla-felles-data-delt/person_data_p2022_v1.parquet",
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/person_data_p2021_v3.parquet",
        "buckets/produkt/test-2/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
    ],
)
def test_invalid_directory(data: str):
    assert check_naming_standard(data) == [
        MISSING_DATA_STATE,
        MISSING_SHORT_NAME,
    ]


@pytest.mark.parametrize(
    ("data"),
    [
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/utdata/person_data_v1.parquet",
    ],
)
def test_invalid_date(data: str):
    assert check_naming_standard(data) == [MISSING_PERIOD]


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
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/utdata/person_data_p2021_v2.parquet",
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/utdata/person_data_p2021_p2022_v2.parquet",
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/utdata/undermappe/person_data_p2021_v2.parquet",
    ],
)
def test_valid_names(data: str):
    assert check_naming_standard(data) == NAME_STANDARD_SUCSESS


@pytest.mark.parametrize(
    ("data"),
    [
        "buckets/inndata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "buckets/klargjorte-data/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "buckets/utdata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "buckets/utdata/person_testdata_p2021-12-31_p2021-12-31_v1",
        "buckets/utdata/dapla/person_testdata_p2021-12-31_p2021-12-31_v1",
        "buckets/oppdrag/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
    ],
)
def test_names_buckets(data: str):
    assert check_naming_standard(data) == NAME_STANDARD_SUCSESS


@pytest.mark.parametrize(
    ("data"),
    [
        "ssb-dapla-example-data-produkt-prod/ledstill/inndata/skjema_p2018_p2020_v1",
        "/buckets/produkt/datadoc/brukertest/1/sykefratot/klargjorte_data/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "buckets/produkt/datadoc/brukertest/1/sykefratot/klargjorte_data/person_testdata_p2021-12-31_p2021-12-31_v1.json",
    ],
)
def test_names_partioned(data: str):
    assert check_naming_standard(data) == NAME_STANDARD_SUCSESS


@pytest.mark.parametrize(
    ("data"),
    [
        "ssb-dapla-example-data-produkt-prod/ledstill/oppdrag/skjema_p2018_p2020_v1",
    ],
)
def test_names_optional_dir(data: str):
    assert check_naming_standard(data) == [
        MISSING_DATA_STATE,
        MISSING_SHORT_NAME,
    ]


@pytest.mark.parametrize(
    ("data"),
    [
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/temp/skjema_p2018_p2020_v1",
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/inndata/temp/skjema_p2018_p2020_v2",
    ],
)
def test_names_temp_dir(data: str):
    assert check_naming_standard(data) == PATH_IGNORED


@pytest.mark.parametrize(
    ("data"),
    [
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/kildedata/skjema_p2018_p2020_v1",
    ],
)
def test_names_source_data_dir(data: str):
    assert check_naming_standard(data) == PATH_IGNORED


@pytest.mark.parametrize(
    ("data"),
    [
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/kildedata/skjema_v1",
    ],
)
def test_source_data_is_ignored(data: str):
    assert check_naming_standard(data) == PATH_IGNORED


@pytest.mark.parametrize(
    ("data"),
    [
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/utdata/persån_testdata_p2021-12-31_p2021-12-31_v1.parquet",
    ],
)
def test_invalid_symbols(data: str):
    assert check_naming_standard(data) == NAME_STANDARD_SUCSESS
