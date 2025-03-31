from pathlib import Path

import pytest

from dapla_metadata.standards.name_validator import ValidationResult
from dapla_metadata.standards.standard_validators import check_naming_standard
from dapla_metadata.standards.standard_validators import generate_validation_report
from dapla_metadata.standards.utils.constants import FILE_DOES_NOT_EXIST
from dapla_metadata.standards.utils.constants import FILE_IGNORED
from dapla_metadata.standards.utils.constants import INVALID_SYMBOLS
from dapla_metadata.standards.utils.constants import MISSING_DATA_STATE
from dapla_metadata.standards.utils.constants import MISSING_DATASET_SHORT_NAME
from dapla_metadata.standards.utils.constants import MISSING_PERIOD
from dapla_metadata.standards.utils.constants import MISSING_SHORT_NAME
from dapla_metadata.standards.utils.constants import NAME_STANDARD_SUCCESS
from dapla_metadata.standards.utils.constants import PATH_IGNORED

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.parametrize(
    ("file_path"),
    [
        "buckets/data/sirkus/utdata/person_data_p2021_v2.parquet",
    ],
)
@pytest.mark.asyncio
async def test_non_existent_path(file_path: str):
    results = await check_naming_standard(file_path=file_path)
    assert len(results) == 1
    assert results[0].messages[0] == FILE_DOES_NOT_EXIST
    assert results[0].success


@pytest.mark.parametrize(
    ("file_path"),
    [
        "ssb-staging-dapla-felles-data-delt/datadoc/utdata/person_data_v1.parquet",
        "dataset/klargjorte_data/arbmark/resources/person_data_v1.parquet",
    ],
)
@pytest.mark.asyncio
async def test_missing_date_period(file_path, tmp_path):
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.touch()
    assert (await check_naming_standard(file_path=full_path))[0].violations == [
        MISSING_PERIOD,
    ]


@pytest.mark.parametrize(
    ("file_path"),
    [
        "gs://ssb-staging-dapla-felles-data-delt/stat_reg/person_data_p2022_v1.parquet",
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/person_data_p2021_v3.parquet",
        "buckets/produkt/test-2/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
    ],
)
@pytest.mark.asyncio
async def test_missing_data_state(file_path, tmp_path):
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.touch()
    assert (
        MISSING_DATA_STATE
        in (await check_naming_standard(file_path=full_path))[0].violations
    )


@pytest.mark.parametrize(
    ("file_path"),
    [
        "buckets/stat/inndata/person_data_p2022_v1.parquet",
        "gs://ssb-staging-dapla-felles-data-delt/inndata/person_data_p2022_v1.parquet",
        "gs://ssb-staging-dapla-felles-data-delt/klargjorte-data/person_data_p2021_v3.parquet",
        "buckets/produkt/utdata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
    ],
)
@pytest.mark.asyncio
async def test_missing_shortname(file_path, tmp_path):
    test_file = tmp_path / file_path
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.touch()
    assert (await check_naming_standard(file_path=test_file))[0].violations == [
        MISSING_SHORT_NAME,
    ]


@pytest.mark.parametrize(
    ("file_path"),
    [
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/temp/skjema_v1.parquet",
        "gs:/ssb-dapla-example-data-produkt-prod/ledstill/temp/skjema_v1.parquet",
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/inndata/temp/skjema_p2018_p2020_v2.parquet",
        "gs://ssb-dapla-example-data-produkt-prod/temp/ledstill/inndata/temp/skjema_p2018_p2020",
        "gs://ssb-dapla-example-data-produkt-prod/konfigurasjon/ledstill/inndata/skjema_p2018_p2020",
    ],
)
@pytest.mark.asyncio
async def test_ignored_paths(file_path, tmp_path):
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.touch()
    assert (await check_naming_standard(file_path=full_path))[0].messages[
        0
    ] == PATH_IGNORED


@pytest.mark.parametrize(
    ("file_path"),
    [
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/utdata/persån_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "gs://ssb-dapla-example-data-prædukt-prod/ledstill/utdata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
    ],
)
@pytest.mark.asyncio
async def test_invalid_symbols(file_path, tmp_path):
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.touch()
    result = await check_naming_standard(file_path=full_path)
    assert any(v for v in result[0].violations for v in [INVALID_SYMBOLS])


@pytest.mark.parametrize(
    ("file_path"),
    [
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/utdata/p2021_v2.parquet",
        "buckets/produkt/datadoc/brukertest/1/sykefratot/klargjorte_data/_p2021-12-31_p2021-12-31_v1.parquet",
    ],
)
@pytest.mark.asyncio
async def test_missing_dataset_shortname(file_path, tmp_path):
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.touch()
    result = await check_naming_standard(file_path=full_path)
    assert any(v for v in result[0].violations for v in [MISSING_DATASET_SHORT_NAME])


@pytest.mark.parametrize(
    ("file_path"),
    [
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/utdata/p2021_v2.parquet",
        "buckets/produkt/datadoc/brukertest/1/sykefratot/klargjorte_data/_p2021-12-31_p2021-12-31_v1.parquet",
    ],
)
@pytest.mark.asyncio
async def test_missing_dataset_shortname_as_dict(file_path, tmp_path):
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.touch()
    result = await check_naming_standard(file_path=full_path)
    assert not result[0].to_dict()["success"]


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
@pytest.mark.asyncio
async def test_missing_multiple(file_path: str, violations: list, tmp_path):
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.touch()
    result = await check_naming_standard(file_path=full_path)
    if isinstance(result[0], ValidationResult):
        assert any(v for v in result[0].violations for v in violations)


@pytest.mark.parametrize(
    ("file_path"),
    [
        "buckets/produkt/datadoc/utdata/person_data_p2021_v2.parquet",
        "produkt/datadoc/utdata/person_data_p2021_p2022_v2.parquet",
        "datadoc/utdata/undermappe/person_data_p2021_v2.parquet",
        "delt-data/dataset/klargjorte_data/arbmark/resources/person_data_p2021-12-31_p2021-12-31_v1.parquet",
        "stat/inndata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "ssb-delt/stat/klargjorte-data/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "produkt-delt/datadoc/brukertest/1/sykefratot/klargjorte_data/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
    ],
)
@pytest.mark.asyncio
async def test_check_naming_standard_specific_file_path(
    file_path: str,
    tmp_path: Path,
):
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.touch()
    results = await check_naming_standard(
        full_path,
    )
    assert len(results) == 1
    for r in results:
        assert r.success
        assert NAME_STANDARD_SUCCESS in r.messages


@pytest.mark.parametrize(
    ("file_path"),
    [
        "buckets/produkt/datadoc/utdata/person_data_p2021_v2.csv",
        "samfunns-produkt/datadoc/brukertest/1/sykefratot/klargjorte_data/person_testdata_p2021-12-31_p2021-12-31_v1.json",
    ],
)
@pytest.mark.asyncio
async def test_check_naming_standard_ignored_file_type(
    file_path: str,
    tmp_path: Path,
):
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.touch()
    results = await check_naming_standard(
        full_path,
    )
    assert len(results) == 1
    for r in results:
        assert r.success
        assert FILE_IGNORED in r.messages


@pytest.mark.parametrize(
    ("short_name", "file_path_1", "file_path_2", "bucket_name", "expect_success"),
    [
        (
            "stat_reg",
            "person_data_p2022_v1.parquet",
            "bil_data_p2022_v1.parquet",
            "ssb-staging-dapla-felles-data-delt",
            True,
        ),
        (
            "temp_stuff",
            "_p2022_v1.parquet",
            "bil_data_v1.parquet",
            "ssb-staging-dapla-felles-data-delt",
            False,
        ),
    ],
)
@pytest.mark.asyncio
async def test_check_naming_directory_with_subdirectories(
    short_name: str,
    file_path_1: str,
    file_path_2: str,
    bucket_name: str,
    expect_success: bool,
    tmp_path: Path,
):
    fake_bucket = tmp_path / bucket_name / short_name

    indata_path = fake_bucket / "inndata"
    outdata_path = fake_bucket / "utdata"

    indata_path.mkdir(parents=True, exist_ok=True)
    outdata_path.mkdir(parents=True, exist_ok=True)

    (indata_path / file_path_1).touch()
    (indata_path / file_path_2).touch()
    (outdata_path / file_path_1).touch()
    (outdata_path / file_path_2).touch()
    results = await check_naming_standard(
        tmp_path / bucket_name,
    )
    assert len(results) == 4
    for r in results:
        if expect_success:
            assert r.success
            assert NAME_STANDARD_SUCCESS in r.messages
            r.file_path.startswith(str(fake_bucket))
        else:
            assert not r.success
            assert len(r.violations) > 0
            assert (
                MISSING_DATASET_SHORT_NAME in r.violations
                or MISSING_PERIOD in r.violations
            )


@pytest.mark.parametrize(
    ("file_path", "violations"),
    [
        (
            "gs://ssb-dapla-example-data-produkt-prod/inndata/skjema_p2021-12-31_p2021-12-31_v1.parquet",
            [MISSING_SHORT_NAME],
        ),
        (
            "gs://ssb-dapla-example-data-produkt-prod/inndata/mappe/skjema_p2021-12-31_p2021-12-31_v1.parquet",
            [MISSING_SHORT_NAME],
        ),
        (
            "gs://inndata/skjema_p2021-12-31_p2021-12-31_v1.parquet",
            [MISSING_SHORT_NAME],
        ),
        (
            "buckets/produkt/klargjorte_data/bil_p2021-12-31_p2021-12-31_v1.parquet",
            [MISSING_SHORT_NAME],
        ),
        (
            "gs://ssb-dapla-example-data-produkt-prod/ledstill/skjema_p2021-12-31_p2021-12-31_v1.parquet",
            [MISSING_DATA_STATE],
        ),
        (
            "buckets/produkt/ledstill/bil_p2021-12-31_p2021-12-31_v1.parquet",
            [MISSING_DATA_STATE],
        ),
        (
            "buckets/bil_p2021-12-31_p2021-12-31_v1.parquet",
            [MISSING_SHORT_NAME, MISSING_DATA_STATE],
        ),
    ],
)
@pytest.mark.asyncio
async def test_validate_short_name(file_path: str, violations: list, tmp_path):
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.touch()

    result = await check_naming_standard(file_path=full_path)
    if isinstance(result, ValidationResult):
        assert result.violations == violations


@pytest.mark.asyncio
async def test_generate_naming_standard_report(tmp_path):
    file_paths = [
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/inndata/skjema_p1988_v1.parquet",
        "buckets/ssb-dapla-example-data-produkt-prod/inndata/skjema_v2.parquet",
        "buckets/ssb-dapla-example-data-produkt-prod/utdata/editert_v1.parquet",
        "buckets/ssb-dapla-example-data-produkt-prod/klargjorte_data/_p2021-12-31_p2021-12-31_v1.parquet",
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/klargjorte_data/park_p2021-12-31_p2021-12-31_v1.parquet",
    ]
    for file_path in file_paths:
        full_path = tmp_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.touch()

    results = await check_naming_standard(
        file_path=str(tmp_path / "buckets/ssb-dapla-example-data-produkt-prod"),
    )

    if isinstance(results, list):
        report = generate_validation_report(validation_results=results)
        assert report.num_failures == 3
        assert report.num_files_validated == 5
        assert report.num_success == 2
