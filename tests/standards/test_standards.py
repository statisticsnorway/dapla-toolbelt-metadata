import pytest

from dapla_metadata.standards.name_validator import ValidationResult
from dapla_metadata.standards.standard_validators import check_naming_standard
from dapla_metadata.standards.utils.constants import FILE_PATH_NOT_CONFIRMED
from dapla_metadata.standards.utils.constants import INVALID_SYMBOLS
from dapla_metadata.standards.utils.constants import MISSING_DATA_STATE
from dapla_metadata.standards.utils.constants import MISSING_DATASET_SHORT_NAME
from dapla_metadata.standards.utils.constants import MISSING_PERIOD
from dapla_metadata.standards.utils.constants import MISSING_SHORT_NAME
from dapla_metadata.standards.utils.constants import NAME_STANDARD_SUCSESS
from dapla_metadata.standards.utils.constants import PATH_IGNORED


@pytest.mark.parametrize(
    ("file_path"),
    [
        "buckets/produkt/datadoc/utdata/person_data_p2021_v2.parquet",
        "produkt/datadoc/utdata/person_data_p2021_p2022_v2.parquet",
        "datadoc/utdata/undermappe/person_data_p2021_v2.parquet",
        "delt-data/dataset/klargjorte_data/arbmark/resources/person_data_p2021-12-31_p2021-12-31_v1.parquet",
        "stat/inndata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "ssb-delt/stat/klargjorte-data/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "ssb-test/ledstill/inndata/skjema_p2018_p2020_v1",
        "produkt-delt/datadoc/brukertest/1/sykefratot/klargjorte_data/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "samfunns-produkt/datadoc/brukertest/1/sykefratot/klargjorte_data/person_testdata_p2021-12-31_p2021-12-31_v1.json",
    ],
)
def test_valid_path(file_path, tmp_path):
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.touch()
    result = check_naming_standard(file_path=full_path)
    assert result.messages == [
        NAME_STANDARD_SUCSESS,
    ]
    assert isinstance(result, ValidationResult)


@pytest.mark.parametrize(
    ("file_path"),
    [
        "buckets/produkt/datadoc/utdata/person_data_p2021_v2.parquet",
        "datadoc/utdata/person_data_p2021_p2022_v2.parquet",
        "datadoc/utdata/undermappe/person_data_p2021_v2.parquet",
        "dataset/klargjorte_data/arbmark/resources/person_data_p2021-12-31_p2021-12-31_v1.parquet",
        "stat/inndata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "stat/klargjorte-data/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "ledstill/inndata/skjema_p2018_p2020_v1",
        "datadoc/brukertest/1/sykefratot/klargjorte_data/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "datadoc/brukertest/1/sykefratot/klargjorte_data/person_testdata_p2021-12-31_p2021-12-31_v1.json",
    ],
)
def test_valid_path_string_result(file_path, tmp_path):
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.touch()
    assert check_naming_standard(file_path=full_path).messages == [
        NAME_STANDARD_SUCSESS,
    ]


@pytest.mark.parametrize(
    ("file_path"),
    [
        "buckets/data/sirkus/utdata/person_data_p2021_v2.parquet",
    ],
)
def test_path_not_confirmed(file_path):
    assert (
        check_naming_standard(file_path=file_path).messages[0]
        == FILE_PATH_NOT_CONFIRMED
    )


@pytest.mark.parametrize(
    ("file_path"),
    [
        "ssb-staging-dapla-felles-data-delt/datadoc/utdata/person_data_v1.parquet",
        "dataset/klargjorte_data/arbmark/resources/person_data_v1.parquet",
    ],
)
def test_missing_date_period(file_path, tmp_path):
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.touch()
    assert check_naming_standard(file_path=full_path).violations == [MISSING_PERIOD]


@pytest.mark.parametrize(
    ("file_path"),
    [
        "gs://ssb-staging-dapla-felles-data-delt/stat_reg/person_data_p2022_v1.parquet",
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/person_data_p2021_v3.parquet",
        "buckets/produkt/test-2/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
    ],
)
def test_missing_data_state(file_path, tmp_path):
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.touch()
    assert MISSING_DATA_STATE in check_naming_standard(file_path=full_path).violations


@pytest.mark.parametrize(
    ("file_path"),
    [
        "buckets/stat/inndata/person_data_p2022_v1.parquet",
        "gs://ssb-staging-dapla-felles-data-delt/inndata/person_data_p2022_v1.parquet",
        "gs://ssb-staging-dapla-felles-data-delt/klargjorte-data/person_data_p2021_v3.parquet",
        "buckets/produkt/utdata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
    ],
)
def test_missing_shortname(file_path, tmp_path):
    test_file = tmp_path / file_path
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.touch()
    assert check_naming_standard(file_path=test_file).violations == [MISSING_SHORT_NAME]


@pytest.mark.parametrize(
    ("file_path"),
    [
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/temp/skjema_v1.parquet",
        "gs:/ssb-dapla-example-data-produkt-prod/ledstill/temp/skjema_v1.parquet",
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/inndata/temp/skjema_p2018_p2020_v2.parquet",
        "gs://ssb-dapla-example-data-produkt-prod/temp/ledstill/inndata/temp/skjema_p2018_p2020",
        "gs://ssb-dapla-example-data-produkt-prod/konfigurasjon/ledstill/inndata/skjema_p2018_p2020",
        "gs://ssb-dapla-example-data-produkt-prod/Konfigurasjon/ledstill/inndata/skjema_p2018_p2020",
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/kildedata/skjema_v1",
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/kildedata/skjema_p2018_p2020_v1",
        "gs://ssb-dapla-example-data-produkt-prod/ledstill/kildedata/skjema_p2018_p2020_v1",
    ],
)
def test_ignored_paths(file_path, tmp_path):
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.touch()
    assert check_naming_standard(file_path=full_path).messages[0] == PATH_IGNORED


@pytest.mark.parametrize(
    ("file_path"),
    [
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/utdata/persån_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "gs://ssb-dapla-example-data-prædukt-prod/ledstill/utdata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
    ],
)
def test_invalid_symbols(file_path, tmp_path):
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.touch()
    result = check_naming_standard(file_path=full_path)
    assert any(v for v in result.violations for v in [INVALID_SYMBOLS])


@pytest.mark.parametrize(
    ("file_path"),
    [
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/utdata/p2021_v2.parquet",
        "buckets/produkt/datadoc/brukertest/1/sykefratot/klargjorte_data/_p2021-12-31_p2021-12-31_v1.json",
    ],
)
def test_missing_dataset_shortname(file_path, tmp_path):
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.touch()
    result = check_naming_standard(file_path=full_path)
    assert any(v for v in result.violations for v in [MISSING_DATASET_SHORT_NAME])


@pytest.mark.parametrize(
    ("file_path"),
    [
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/utdata/p2021_v2.parquet",
        "buckets/produkt/datadoc/brukertest/1/sykefratot/klargjorte_data/_p2021-12-31_p2021-12-31_v1.json",
    ],
)
def test_missing_dataset_shortname_as_dict(file_path, tmp_path):
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.touch()
    result = check_naming_standard(file_path=full_path)
    assert not result.to_dict()["success"]


@pytest.mark.parametrize(
    ("file_path", "violations"),
    [
        (
            "gs://ssb-dapla-example-data-produkt-prod/inndata/skjema_v1.parquet",
            [MISSING_SHORT_NAME, MISSING_PERIOD],
        ),
        (
            "gs://inndata/skjema_v1.parquet",
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
    result = check_naming_standard(file_path=full_path)
    if isinstance(result, ValidationResult):
        assert any(v for v in result.violations for v in violations)


@pytest.mark.parametrize(
    ("file_path"),
    [
        "ssb-dapla-example-data-produkt-prod/ledstill/inndata/skjema_p2018_p202_v1/aar=2018/data.parquet",
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/inndata/skjema_p2018_p202_v1/aar=2019/data.parquet",
        "ssb-dapla-example-data-produkt-prod/ledstill/klargjorte_data/editert_p2018_p202_v1/aar=2018/data.parquet",
    ],
)
def test_valid_partioned_path_success(file_path, tmp_path):
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.touch()
    result = check_naming_standard(file_path=full_path)
    assert result.messages == [
        NAME_STANDARD_SUCSESS,
    ]
    assert isinstance(result, ValidationResult)


@pytest.mark.parametrize(
    ("file_path", "violations"),
    [
        (
            "ssb-dapla-example-data-produkt-prod/inndata/skjema_p2018_p202_v1/aar=2018/data.parquet",
            [MISSING_PERIOD, INVALID_SYMBOLS],
        ),
        (
            "buckets/ssb-dapla-example-data-produkt-prod/ledstill/skjema_p2018_p202_v1/aar=2019/data.parquet",
            [MISSING_SHORT_NAME, MISSING_DATA_STATE, MISSING_PERIOD, INVALID_SYMBOLS],
        ),
        (
            "ssb-dapla-example-data-produkt-prod/ledstill/klargjorte_data/editert_v1/aar=2018/data.parquet",
            [MISSING_PERIOD, INVALID_SYMBOLS],
        ),
    ],
)
def test_valid_partioned_path_violations(file_path, violations, tmp_path):
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.touch()
    result = check_naming_standard(file_path=full_path)
    assert result.violations == violations
