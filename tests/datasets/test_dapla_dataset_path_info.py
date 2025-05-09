from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest
from datadoc_model.all_optional.model import DataSetState

from dapla_metadata.datasets.dapla_dataset_path_info import ISO_YEAR
from dapla_metadata.datasets.dapla_dataset_path_info import ISO_YEAR_MONTH
from dapla_metadata.datasets.dapla_dataset_path_info import ISO_YEAR_MONTH_DAY
from dapla_metadata.datasets.dapla_dataset_path_info import SSB_BIMESTER
from dapla_metadata.datasets.dapla_dataset_path_info import DaplaDatasetPathInfo
from tests.datasets.constants import TEST_BUCKET_PARQUET_FILEPATH_WITH_SHORTNAME
from tests.datasets.constants import TEST_PARQUET_FILEPATH

if TYPE_CHECKING:
    import pathlib


@dataclass
class DatasetPathTestCase:
    """Structure to define attributes needed for a test case."""

    path: str
    expected_contains_data_from: datetime.date
    expected_contains_data_until: datetime.date


TEST_CASES = [
    DatasetPathTestCase(
        path="grensehandel_imputert_p2022-10-01_p2022-12-31_v1.parquet",
        expected_contains_data_from=datetime.date(2022, 10, 1),
        expected_contains_data_until=datetime.date(2022, 12, 31),
    ),
    DatasetPathTestCase(
        path="grensehandel_imputert_p2022-10_p2022-12_v1.parquet",
        expected_contains_data_from=datetime.date(2022, 10, 1),
        expected_contains_data_until=datetime.date(2022, 12, 31),
    ),
    DatasetPathTestCase(
        path="flygende_objekter_p2019_v1.parquet",
        expected_contains_data_from=datetime.date(2019, 1, 1),
        expected_contains_data_until=datetime.date(2019, 12, 31),
    ),
    DatasetPathTestCase(
        path="framskrevne-befolkningsendringer_p2019_p2050_v1.parquet",
        expected_contains_data_from=datetime.date(2019, 1, 1),
        expected_contains_data_until=datetime.date(2050, 12, 31),
    ),
    DatasetPathTestCase(
        path="ufo_observasjoner_p2019_p2020_v1.parquet",
        expected_contains_data_from=datetime.date(2019, 1, 1),
        expected_contains_data_until=datetime.date(2020, 12, 31),
    ),
    DatasetPathTestCase(
        path="omsetning_p2020W15_v1.parquet",
        expected_contains_data_from=datetime.date(2020, 4, 6),
        expected_contains_data_until=datetime.date(2020, 4, 12),
    ),
    DatasetPathTestCase(
        path="omsetning_p1981-W52_v1.parquet",
        expected_contains_data_from=datetime.date(1981, 12, 21),
        expected_contains_data_until=datetime.date(1981, 12, 27),
    ),
    DatasetPathTestCase(
        path="personinntekt_p2022H1_v1.parquet",
        expected_contains_data_from=datetime.date(2022, 1, 1),
        expected_contains_data_until=datetime.date(2022, 6, 30),
    ),
    DatasetPathTestCase(
        path="personinntekt_p2022-H1_v1.parquet",
        expected_contains_data_from=datetime.date(2022, 1, 1),
        expected_contains_data_until=datetime.date(2022, 6, 30),
    ),
    DatasetPathTestCase(
        path="nybilreg_p2022T1_v1.parquet",
        expected_contains_data_from=datetime.date(2022, 1, 1),
        expected_contains_data_until=datetime.date(2022, 4, 30),
    ),
    DatasetPathTestCase(
        path="nybilreg_p2022-T1_v1.parquet",
        expected_contains_data_from=datetime.date(2022, 1, 1),
        expected_contains_data_until=datetime.date(2022, 4, 30),
    ),
    DatasetPathTestCase(
        path="varehandel_p2018Q1_p2018Q4_v1.parquet",
        expected_contains_data_from=datetime.date(2018, 1, 1),
        expected_contains_data_until=datetime.date(2018, 12, 31),
    ),
    DatasetPathTestCase(
        path="varehandel_p2018-Q1_p2018-Q4_v1.parquet",
        expected_contains_data_from=datetime.date(2018, 1, 1),
        expected_contains_data_until=datetime.date(2018, 12, 31),
    ),
    DatasetPathTestCase(
        path="pensjon_p2018Q1_v1.parquet",
        expected_contains_data_from=datetime.date(2018, 1, 1),
        expected_contains_data_until=datetime.date(2018, 3, 31),
    ),
    DatasetPathTestCase(
        path="pensjon_p2018-Q1_v1.parquet",
        expected_contains_data_from=datetime.date(2018, 1, 1),
        expected_contains_data_until=datetime.date(2018, 3, 31),
    ),
    DatasetPathTestCase(
        path="skipsanloep_p2021B2_v1.parquet",
        expected_contains_data_from=datetime.date(2021, 3, 1),
        expected_contains_data_until=datetime.date(2021, 4, 30),
    ),
    DatasetPathTestCase(
        path="skipsanloep_p2021-B2_v1.parquet",
        expected_contains_data_from=datetime.date(2021, 3, 1),
        expected_contains_data_until=datetime.date(2021, 4, 30),
    ),
    DatasetPathTestCase(
        path="skipsanloep_p2022B1_v1.parquet",
        expected_contains_data_from=datetime.date(2022, 1, 1),
        expected_contains_data_until=datetime.date(2022, 2, 28),
    ),
    DatasetPathTestCase(
        path="skipsanloep_p2022-B1_v1.parquet",
        expected_contains_data_from=datetime.date(2022, 1, 1),
        expected_contains_data_until=datetime.date(2022, 2, 28),
    ),
]


@pytest.fixture(
    ids=[tc.path for tc in TEST_CASES],
    params=TEST_CASES,
)
def test_data(request: pytest.FixtureRequest) -> DatasetPathTestCase:
    return request.param


@pytest.fixture
def dataset_path(test_data: DatasetPathTestCase) -> DaplaDatasetPathInfo:
    return DaplaDatasetPathInfo(test_data.path)


@pytest.fixture
def expected_contains_data_from(test_data: DatasetPathTestCase) -> datetime.date:
    return test_data.expected_contains_data_from


@pytest.fixture
def expected_contains_data_until(test_data: DatasetPathTestCase) -> datetime.date:
    return test_data.expected_contains_data_until


def test_extract_period_info_date_from(
    dataset_path: DaplaDatasetPathInfo,
    expected_contains_data_from: datetime.date,
):
    assert dataset_path.contains_data_from == expected_contains_data_from


def test_extract_period_info_date_until(
    dataset_path: DaplaDatasetPathInfo,
    expected_contains_data_until: datetime.date,
):
    assert dataset_path.contains_data_until == expected_contains_data_until


@pytest.mark.parametrize(
    "data",
    [
        "nonsen.data",
        "nonsens2.parquet",
        TEST_PARQUET_FILEPATH.name,
    ],
)
def test_extract_period_info_no_period_info_in_path(data: str):
    assert DaplaDatasetPathInfo(data).contains_data_from is None


@pytest.mark.parametrize(
    ("path_parts_to_insert", "expected_result"),
    [
        ("kildedata", DataSetState.SOURCE_DATA),
        ("inndata", DataSetState.INPUT_DATA),
        ("roskildedata/klargjorte-data", DataSetState.PROCESSED_DATA),
        ("klargjorte_data", DataSetState.PROCESSED_DATA),
        ("klargjorte-data", DataSetState.PROCESSED_DATA),
        ("statistikk", DataSetState.STATISTICS),
        ("", None),
    ],
)
def test_get_dataset_state(
    full_dataset_state_path: pathlib.Path,
    expected_result: DataSetState,
):
    actual_state = DaplaDatasetPathInfo(full_dataset_state_path).dataset_state
    assert actual_state == expected_result


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("person_data_v1", "1"),
        ("person_data_v2", "2"),
        ("person_data_vwrong", None),
        ("person_data", None),
        ("person_testdata_p2021-12-31_p2021-12-31_v20", "20"),
    ],
)
def test_get_dataset_version(
    path: str,
    expected: str | None,
):
    assert DaplaDatasetPathInfo(path).dataset_version == expected


# These tests covers both date until after date from, mix of SSB keys and invalid SSB keys
@pytest.mark.parametrize(
    "dataset_path_name",
    [
        "ufo_observasjoner_p2019_p1920_v1.parquet",
        "varehandel_p2018H2_p2018H1_v1.parquet",
        "varehandel_p2018Q1_p2018H2_v1.parquet",
        "sykkeltransport_p1973B8_v1.parquet",
    ],
)
def test_extract_period_info_date_from_invalid_pathname(dataset_path_name: str) -> None:
    dataset = DaplaDatasetPathInfo(dataset_path_name)
    assert dataset.contains_data_from is None


@pytest.mark.parametrize(
    "dataset_path_name",
    [
        "ufo_observasjoner_p2019_p1920_v1.parquet",
        "varehandel_p2018H2_p2018H1_v1.parquet",
        "varehandel_p2018Q1_p2018H2_v1.parquet",
        "sykkeltransport_p1973B2_p2020T8_v1.parquet",
    ],
)
def test_extract_period_info_date_until_invalid_pathname(
    dataset_path_name: str,
) -> None:
    dataset = DaplaDatasetPathInfo(dataset_path_name)
    assert dataset.contains_data_until is None


@pytest.mark.parametrize(
    ("date_format", "period"),
    [
        (ISO_YEAR, "1980"),
        (ISO_YEAR_MONTH, "1888-11"),
        (ISO_YEAR_MONTH_DAY, "2203-01-24"),
        (SSB_BIMESTER, "1963B3"),
    ],
)
def test_date_format_return_date_object_period_start(date_format, period):
    assert isinstance(date_format.get_floor(period), datetime.date)


@pytest.mark.parametrize(
    ("date_format", "period"),
    [
        (ISO_YEAR, "1980"),
        (ISO_YEAR_MONTH, "1888-11"),
        (ISO_YEAR_MONTH_DAY, "2203-01-24"),
        (SSB_BIMESTER, "1963B3"),
    ],
)
def test_date_format_return_date_object_period_end(date_format, period):
    assert isinstance(date_format.get_ceil(period), datetime.date)


@pytest.mark.parametrize(
    ("date_format", "period", "expected"),
    [
        (ISO_YEAR, "1980", datetime.date(1980, 1, 1)),
        (ISO_YEAR_MONTH, "1888-11", datetime.date(1888, 11, 1)),
        (ISO_YEAR_MONTH_DAY, "2203-01-24", datetime.date(2203, 1, 24)),
        (SSB_BIMESTER, "1963B3", datetime.date(1963, 5, 1)),
    ],
)
def test_date_format_correct_from_date(date_format, period, expected: datetime.date):
    assert date_format.get_floor(period) == expected


@pytest.mark.parametrize(
    ("date_format", "period", "expected"),
    [
        (ISO_YEAR, "1980", datetime.date(1980, 12, 31)),
        (ISO_YEAR_MONTH, "1888-11", datetime.date(1888, 11, 30)),
        (ISO_YEAR_MONTH_DAY, "2203-01-24", datetime.date(2203, 1, 24)),
        (SSB_BIMESTER, "1963B3", datetime.date(1963, 6, 30)),
    ],
)
def test_date_format_correct_end_date(date_format, period, expected):
    assert date_format.get_ceil(period) == expected


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (TEST_BUCKET_PARQUET_FILEPATH_WITH_SHORTNAME, "befolkning"),
        (
            "gs://ssb-staging-dapla-felles-data-delt/datadoc/person_data_v1.parquet",
            "datadoc",
        ),
        ("inndata/person_data_v1.parquet", None),
        ("stat/inndata/person_data", "stat"),
        ("buckets/stat/inndata/person_data", None),
        ("buckets/bucket_name/stat/inndata/person_data", "stat"),
    ],
)
def test_extract_shortname_in_path(data: str, expected: str):
    assert DaplaDatasetPathInfo(data).statistic_short_name == expected


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (
            TEST_BUCKET_PARQUET_FILEPATH_WITH_SHORTNAME,
            "ssb-staging-dapla-felles-data-delt",
        ),
        (
            "gs://datadoc/person_data_v1.parquet",
            "datadoc",
        ),
        (
            "buckets/ssb-bucket/stat_name/klargjorte_data/person_data_p2021-12-31_p2021-12-31_v1.parquet",
            "ssb-bucket",
        ),
    ],
)
def test_extract_bucketname_in_path(data: str, expected: str):
    assert DaplaDatasetPathInfo(data).bucket_name == expected


@pytest.mark.parametrize(
    ("data"),
    [
        "gs://ssb-staging-dapla-felles-data-delt/person_data_p2022_v1.parquet",
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/person_data_v1.parquet",
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/person_data_p2021_v3.parquet",
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/utdata/person_data_v1.parquet",
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/utdata/person_data_p2021.parquet",
        "gs://utdata/person_data_p2021_p2022_v2.parquet",
        "buckets/klargjorte_data/person_data_p2021-12-31_p2021-12-31_v1.parquet",
    ],
)
def test_path_complies_with_naming_standard_invalid_input(data: str):
    assert DaplaDatasetPathInfo(data).path_complies_with_naming_standard() is False


@pytest.mark.parametrize(
    ("data"),
    [
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/utdata/person_data_p2021_v2.parquet",
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/utdata/person_data_p2021_p2022_v2.parquet",
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/utdata/undermappe/person_data_p2021_v2.parquet",
        "buckets/bucket_name/dataset/klargjorte_data/person_data_p2021-12-31_p2021-12-31_v1.parquet",
        "dataset/klargjorte_data/person_data_p2021-12-31_p2021-12-31_v1.parquet",
    ],
)
def test_path_complies_with_naming_standard_valid_input(data: str):
    assert DaplaDatasetPathInfo(data).path_complies_with_naming_standard() is True
