import pytest

from dapla_metadata.dapla.name_validator import INVALID_SYMBOLS
from dapla_metadata.dapla.name_validator import MISSING_DATA_STATE
from dapla_metadata.dapla.name_validator import MISSING_PERIOD
from dapla_metadata.dapla.name_validator import MISSING_SHORT_NAME
from dapla_metadata.dapla.name_validator import NAME_STANDARD_SUCSESS
from dapla_metadata.dapla.name_validator import PATH_IGNORED
from dapla_metadata.dapla.standards import check_naming_standard


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
