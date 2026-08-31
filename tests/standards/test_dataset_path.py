import pytest

from dapla_metadata.standards import DataState
from dapla_metadata.standards import FileType
from dapla_metadata.standards import dataset_path
from dapla_metadata.standards.dataset_path import _validate_data_state
from dapla_metadata.standards.dataset_path import _validate_file_type
from dapla_metadata.standards.dataset_path import _validate_folders
from dapla_metadata.standards.dataset_path import _validate_periods
from dapla_metadata.standards.dataset_path import _validate_product
from dapla_metadata.standards.dataset_path import _validate_short_description
from dapla_metadata.standards.dataset_path import _validate_version


@pytest.mark.parametrize(
    ("metadata", "expected"),
    [
        (
            {
                "bucket": "ssb-dapla-example-data-produkt-prod",
                "product": "ledstill",
                "data_state": DataState.OUTPUT_DATA,
                "short_description": "varehandel",
                "period_from": "2018-Q1",
                "version": 3,
                "file_type": FileType.PARQUET,
            },
            "gs://ssb-dapla-example-data-produkt-prod/ledstill/utdata/varehandel_p2018-Q1_v3.parquet",
        ),
        (
            {
                "bucket": "bucket",
                "product": "ledstill",
                "data_state": DataState.INPUT_DATA,
                "short_description": "flygende-objekter",
                "period_from": "2019",
                "version": 1,
                "file_type": FileType.PARQUET,
            },
            "gs://bucket/ledstill/inndata/flygende-objekter_p2019_v1.parquet",
        ),
        (
            {
                "bucket": "bucket",
                "product": "ledstill",
                "data_state": DataState.PROCESSED_DATA,
                "short_description": "ufo-observasjoner",
                "period_from": "2019",
                "period_to": "2020",
                "version": 1,
                "file_type": FileType.PARQUET,
            },
            "gs://bucket/ledstill/klargjorte-data/ufo-observasjoner_p2019_p2020_v1.parquet",
        ),
        (
            {
                "bucket": "bucket",
                "product": "ledstill",
                "data_state": DataState.STATISTICS,
                "short_description": "grensehandel-imputert",
                "period_from": "2022-10",
                "period_to": "2022-12",
                "version": 1,
                "file_type": FileType.PARQUET,
            },
            "gs://bucket/ledstill/statistikk/grensehandel-imputert_p2022-10_p2022-12_v1.parquet",
        ),
        (
            {
                "bucket": "bucket",
                "product": "ameld_data",
                "data_state": DataState.OUTPUT_DATA,
                "short_description": "omsetning",
                "period_from": "2020-W15",
                "version": 0,
                "file_type": FileType.PARQUET,
            },
            "gs://bucket/ameld_data/utdata/omsetning_p2020-W15_v0.parquet",
        ),
    ],
)
def test_dataset_path_returns_expected_gcs_path(metadata, expected):
    assert dataset_path(**metadata) == expected


@pytest.mark.parametrize("data_state", list(DataState))
def test_dataset_path_supports_canonical_data_states(data_state):
    assert f"/ledstill/{data_state.value}/" in dataset_path(
        bucket="bucket",
        product="ledstill",
        data_state=data_state,
        short_description="varehandel",
        period_from="2018-Q1",
        version=1,
        file_type=FileType.PARQUET,
    )


@pytest.mark.parametrize(
    ("folders", "expected_section"),
    [
        (["dapla"], "/utdata/dapla/varehandel_"),
        (["on-prem", "revidert_data"], "/utdata/on-prem/revidert_data/varehandel_"),
        (["temp"], "/utdata/temp/varehandel_"),
        ([], "/utdata/varehandel_"),
        (None, "/utdata/varehandel_"),
    ],
)
def test_dataset_path_supports_optional_folders(folders, expected_section):
    result = dataset_path(
        bucket="bucket",
        product="ledstill",
        data_state=DataState.OUTPUT_DATA,
        folders=folders,
        short_description="varehandel",
        period_from="2018-Q1",
        version=1,
        file_type=FileType.PARQUET,
    )

    assert expected_section in result


@pytest.mark.parametrize(
    "periods",
    [
        ["2018"],
        ["2018-01"],
        ["2018-01-24"],
        ["2018-015"],
        ["2024-12-31T23-59-30.000"],
        ["2018-W01"],
        ["2018-B1"],
        ["2018-Q1"],
        ["2018-T1"],
        ["2018-H1"],
        ["2018-Q1", "2018-Q4"],
        ["2024-12-31T23-59-30.000", "2024-12-31T23-59-31.000"],
    ],
)
def test_dataset_path_supports_period_formats(periods):
    result = dataset_path(
        bucket="bucket",
        product="ledstill",
        data_state=DataState.OUTPUT_DATA,
        short_description="varehandel",
        period_from=periods[0],
        period_to=periods[1] if len(periods) == 2 else None,
        version=1,
        file_type=FileType.PARQUET,
    )
    assert result.startswith("gs://bucket/ledstill/utdata/varehandel_p")
    assert result.endswith("_v1.parquet")


@pytest.mark.parametrize(
    ("file_type", "suffix"),
    [
        (FileType.JSON, ".json"),
        (FileType.CSV, ".csv"),
        (FileType.XML, ".xml"),
        (FileType.PARQUET, ".parquet"),
    ],
)
def test_dataset_path_supports_file_types(file_type, suffix):
    result = dataset_path(
        bucket="bucket",
        product="ledstill",
        data_state=DataState.OUTPUT_DATA,
        short_description="varehandel",
        period_from="2018-Q1",
        version=1,
        file_type=file_type,
    )

    assert result.endswith(suffix)


@pytest.mark.parametrize(
    ("argument", "value", "message"),
    [
        ("product", "", "Invalid product name"),
        ("product", "product/name", "Invalid product name"),
        ("product", "product with spaces", "Invalid product name"),
        ("short_description", "", "Invalid short description"),
        ("short_description", "name_with_underscore", "Invalid short description"),
        ("short_description", "name with spaces", "Invalid short description"),
        ("short_description", "name/path", "Invalid short description"),
        ("short_description", "påvirket", "Invalid short description"),
        ("bucket", "", "Invalid bucket name"),
        ("bucket", "bucket/nested", "Invalid bucket name"),
        ("bucket", "../escaped", "Invalid bucket name"),
        ("bucket", " bucket ", "Invalid bucket name"),
    ],
)
def test_dataset_path_rejects_invalid_string_values(argument, value, message):
    metadata = {
        "bucket": "bucket",
        "product": "ledstill",
        "data_state": DataState.OUTPUT_DATA,
        "short_description": "varehandel",
        "period_from": "2018-Q1",
        "version": 1,
        "file_type": FileType.PARQUET,
    }
    metadata[argument] = value
    with pytest.raises(ValueError, match=message):
        dataset_path(**metadata)


@pytest.mark.parametrize(
    "data_state", ["utdata", "kildedata", "klargjorte_data", "unknown-state"]
)
def test_dataset_path_rejects_non_enum_data_states(data_state):
    with pytest.raises(TypeError, match="data_state must be a DataState"):
        dataset_path(
            bucket="bucket",
            product="ledstill",
            data_state=data_state,
            short_description="varehandel",
            period_from="2018-Q1",
            version=1,
            file_type=FileType.PARQUET,
        )


@pytest.mark.parametrize(
    ("periods", "message"),
    [
        (["p2018-Q1"], "periods must not include the 'p' prefix"),
        (["2018-Q5"], "Invalid period"),
        (["2018-02-30"], "Invalid period"),
        (["2018-W00"], "Invalid period"),
        (["2018-B7"], "Invalid period"),
        (["2018-T4"], "Invalid period"),
        (["2018-H3"], "Invalid period"),
        (["2018W01"], "Invalid period"),
        (["2018B1"], "Invalid period"),
        (["2018Q1"], "Invalid period"),
        (["2018T1"], "Invalid period"),
        (["2018H1"], "Invalid period"),
        (["2018-000"], "Invalid period"),
        (["2018-366"], "Invalid period"),
        (["2018-01-24 12:34:56"], "Invalid period"),
        (["2018-01-24T12:34"], "Invalid period"),
        (["2018-01-24T12:34:56"], "Invalid period"),
        (["2024-12-31T23-59-30"], "Invalid period"),
        (["2024-12-31T23-59-30.00"], "Invalid period"),
        (["2024-12-31T23-59-30.0000"], "Invalid period"),
        (["2018-Q1", "2018-H2"], "periods must use the same format"),
        (["2018", "2018-12"], "periods must use the same format"),
        (["2019", "2018"], "periods must be in chronological order"),
        (
            ["2024-12-31T23-59-31.000", "2024-12-31T23-59-30.000"],
            "periods must be in chronological order",
        ),
    ],
)
def test_dataset_path_rejects_invalid_periods(periods, message):
    with pytest.raises(ValueError, match=message):
        dataset_path(
            bucket="bucket",
            product="ledstill",
            data_state=DataState.OUTPUT_DATA,
            short_description="varehandel",
            period_from=periods[0],
            period_to=periods[1] if len(periods) == 2 else None,
            version=1,
            file_type=FileType.PARQUET,
        )


@pytest.mark.parametrize("version", [1.5, "1", "v1", True])
def test_dataset_path_rejects_non_integer_versions(version):
    with pytest.raises(TypeError, match="version must be a non-negative integer"):
        dataset_path(
            bucket="bucket",
            product="ledstill",
            data_state=DataState.OUTPUT_DATA,
            short_description="varehandel",
            period_from="2018-Q1",
            version=version,
            file_type=FileType.PARQUET,
        )


def test_dataset_path_rejects_negative_version():
    with pytest.raises(ValueError, match="version must be a non-negative integer"):
        dataset_path(
            bucket="bucket",
            product="ledstill",
            data_state=DataState.OUTPUT_DATA,
            short_description="varehandel",
            period_from="2018-Q1",
            version=-1,
            file_type=FileType.PARQUET,
        )


@pytest.mark.parametrize(
    ("metadata", "expected"),
    [
        ({"bucket": "bucket"}, "gs://bucket"),
        ({"bucket": "bucket", "product": "ledstill"}, "gs://bucket/ledstill"),
        ({"product": "ledstill"}, "ledstill"),
        (
            {"product": "ledstill", "data_state": DataState.OUTPUT_DATA},
            "ledstill/utdata",
        ),
        ({"data_state": DataState.OUTPUT_DATA}, "utdata"),
        (
            {
                "data_state": DataState.OUTPUT_DATA,
                "folders": ["on-prem", "revidert_data"],
            },
            "utdata/on-prem/revidert_data",
        ),
        ({"folders": ["on-prem", "revidert_data"]}, "on-prem/revidert_data"),
        (
            {
                "short_description": "varehandel",
                "period_from": "2018-Q1",
                "version": 1,
                "file_type": FileType.PARQUET,
            },
            "varehandel_p2018-Q1_v1.parquet",
        ),
        (
            {
                "folders": ["on-prem"],
                "short_description": "varehandel",
                "period_from": "2018-Q1",
                "period_to": "2018-Q4",
                "version": 2,
                "file_type": FileType.CSV,
            },
            "on-prem/varehandel_p2018-Q1_p2018-Q4_v2.csv",
        ),
        (
            {
                "data_state": DataState.OUTPUT_DATA,
                "short_description": "varehandel",
                "period_from": "2018-Q1",
                "version": 1,
                "file_type": FileType.PARQUET,
            },
            "utdata/varehandel_p2018-Q1_v1.parquet",
        ),
        (
            {
                "product": "ledstill",
                "data_state": DataState.OUTPUT_DATA,
                "short_description": "varehandel",
                "period_from": "2018-Q1",
                "version": 1,
                "file_type": FileType.PARQUET,
            },
            "ledstill/utdata/varehandel_p2018-Q1_v1.parquet",
        ),
    ],
)
def test_dataset_path_supports_contiguous_partial_paths(metadata, expected):
    assert dataset_path(**metadata) == expected


@pytest.mark.parametrize(
    "metadata",
    [
        {"bucket": "bucket", "data_state": DataState.OUTPUT_DATA},
        {"bucket": "bucket", "folders": ["on-prem"]},
        {
            "bucket": "bucket",
            "short_description": "varehandel",
            "period_from": "2018-Q1",
            "version": 1,
            "file_type": FileType.PARQUET,
        },
        {"product": "ledstill", "folders": ["on-prem"]},
        {
            "product": "ledstill",
            "short_description": "varehandel",
            "period_from": "2018-Q1",
            "version": 1,
            "file_type": FileType.PARQUET,
        },
    ],
)
def test_dataset_path_rejects_gaps_between_supplied_components(metadata):
    with pytest.raises(ValueError, match="required between"):
        dataset_path(**metadata)


@pytest.mark.parametrize(
    "metadata",
    [
        {"short_description": "varehandel"},
        {"period_from": "2018-Q1"},
        {"period_to": "2018-Q4"},
        {"version": 1},
        {"file_type": FileType.PARQUET},
        {
            "short_description": "varehandel",
            "period_from": "2018-Q1",
            "version": 1,
        },
    ],
)
def test_dataset_path_rejects_incomplete_filenames(metadata):
    with pytest.raises(ValueError, match="must be provided together"):
        dataset_path(**metadata)


@pytest.mark.parametrize("metadata", [{}, {"folders": None}, {"folders": []}])
def test_dataset_path_requires_at_least_one_component(metadata):
    with pytest.raises(ValueError, match="At least one path component"):
        dataset_path(**metadata)


def test_dataset_path_rejects_non_string_period_from():
    with pytest.raises(TypeError):
        dataset_path(
            bucket="bucket",
            product="ledstill",
            data_state=DataState.OUTPUT_DATA,
            short_description="varehandel",
            period_from=2018,
            version=1,
            file_type=FileType.PARQUET,
        )


@pytest.mark.parametrize("folders", ["dapla", ("dapla",), [1]])
def test_dataset_path_rejects_invalid_folder_types(folders):
    with pytest.raises(TypeError):
        dataset_path(
            bucket="bucket",
            product="ledstill",
            data_state=DataState.OUTPUT_DATA,
            folders=folders,
            short_description="varehandel",
            period_from="2018-Q1",
            version=1,
            file_type=FileType.PARQUET,
        )


@pytest.mark.parametrize(
    "folder", ["", ".", "..", "mappe/navn", "med mellomrom", "påvirket"]
)
def test_dataset_path_rejects_invalid_folder_names(folder):
    with pytest.raises(ValueError, match="Invalid folder name"):
        dataset_path(
            bucket="bucket",
            product="ledstill",
            data_state=DataState.OUTPUT_DATA,
            folders=[folder],
            short_description="varehandel",
            period_from="2018-Q1",
            version=1,
            file_type=FileType.PARQUET,
        )


def test_dataset_path_requires_keyword_arguments():
    with pytest.raises(TypeError):
        dataset_path(
            "bucket", "ledstill", "utdata", "varehandel", ["2018-Q1"], 1, "parquet"
        )


def test_dataset_path_rejects_naming_syntax_in_inputs():
    with pytest.raises(ValueError, match="Invalid short description"):
        dataset_path(
            bucket="bucket",
            product="ledstill",
            data_state=DataState.OUTPUT_DATA,
            short_description="varehandel/p2018",
            period_from="2018-Q1",
            version=1,
            file_type=".parquet",
        )


@pytest.mark.parametrize("file_type", ["json", ".csv", "PARQUET"])
def test_dataset_path_rejects_non_enum_file_types(file_type):
    with pytest.raises(TypeError, match="file_type must be a FileType"):
        dataset_path(
            bucket="bucket",
            product="ledstill",
            data_state=DataState.OUTPUT_DATA,
            short_description="varehandel",
            period_from="2018-Q1",
            version=1,
            file_type=file_type,
        )


@pytest.mark.parametrize("value", ["ledstill", "ameld_data", "product-2"])
def test_validate_product_accepts_valid_values(value):
    _validate_product(value)


@pytest.mark.parametrize("value", ["", "product/name", "product with spaces"])
def test_validate_product_rejects_invalid_values(value):
    with pytest.raises(ValueError, match="Invalid product name"):
        _validate_product(value)


def test_validate_product_rejects_non_string():
    with pytest.raises(TypeError):
        _validate_product(123)


@pytest.mark.parametrize("value", list(DataState))
def test_validate_data_state_accepts_valid_values(value):
    _validate_data_state(value)


@pytest.mark.parametrize(
    "value", ["", "utdata", "kildedata", "klargjorte_data", "UTDATA", 123]
)
def test_validate_data_state_rejects_non_enum_values(value):
    with pytest.raises(TypeError, match="data_state must be a DataState"):
        _validate_data_state(value)


@pytest.mark.parametrize(
    "value",
    [
        "varehandel",
        "grensehandel-imputert",
        "Name2",
    ],
)
def test_validate_short_description_accepts_valid_values(value):
    _validate_short_description(value)


@pytest.mark.parametrize(
    "value",
    [
        "",
        "name_with_underscore",
        "name with spaces",
        "name/path",
        "name.parquet",
        "å",
        "abc_",
        "abc.",
        "abc/def",
    ],
)
def test_validate_short_description_rejects_invalid_values(value):
    with pytest.raises(ValueError, match="Invalid short description"):
        _validate_short_description(value)


def test_validate_short_description_rejects_non_string():
    with pytest.raises(TypeError):
        _validate_short_description(123)


@pytest.mark.parametrize(
    "value",
    [
        "å",
        "øre",
        "Æra",
        "name_with_underscore",
        "name.parquet",
        "a/b",
        "name with spaces",
        "name@symbol",
        "name#hash",
        "name+plus",
        "name'quote",
        "name:colon",
        "name;semicolon",
        "name\\backslash",
        "name\ttab",
        "name\nnewline",
    ],
)
def test_dataset_path_rejects_short_description_with_illegal_characters(value):
    with pytest.raises(ValueError, match="Invalid short description"):
        dataset_path(
            short_description=value,
            period_from="2025",
            version=0,
            file_type=FileType.JSON,
        )


@pytest.mark.parametrize(
    ("period_from", "period_to"),
    [
        ("2018", None),
        ("2018-Q1", None),
        ("2018-Q1", "2018-Q4"),
        ("2022-01-24", None),
        ("2022-015", None),
        ("2024-12-31T23-59-30.000", None),
    ],
)
def test_validate_periods_accepts_valid_values(period_from, period_to):
    _validate_periods(period_from, period_to)


@pytest.mark.parametrize(
    ("period_from", "period_to", "message"),
    [
        ("p2018", None, "periods must not include the 'p' prefix"),
        ("2018-Q5", None, "Invalid period"),
        ("2018Q1", None, "Invalid period"),
        ("2018-Q1", "2018-H2", "periods must use the same format"),
        ("2018", "2018-12", "periods must use the same format"),
        ("2019", "2018", "periods must be in chronological order"),
    ],
)
def test_validate_periods_rejects_invalid_values(period_from, period_to, message):
    with pytest.raises(ValueError, match=message):
        _validate_periods(period_from, period_to)


@pytest.mark.parametrize("period_from", [2018, ("2018",), [2018]])
def test_validate_periods_rejects_invalid_types(period_from):
    with pytest.raises(TypeError):
        _validate_periods(period_from)


@pytest.mark.parametrize("value", [0, 1, 999])
def test_validate_version_accepts_valid_values(value):
    _validate_version(value)


def test_validate_version_rejects_negative_integer():
    with pytest.raises(ValueError, match="version must be a non-negative integer"):
        _validate_version(-1)


@pytest.mark.parametrize("value", [1.5, "1", "v1", True])
def test_validate_version_rejects_invalid_types(value):
    with pytest.raises(TypeError):
        _validate_version(value)


@pytest.mark.parametrize("value", list(FileType))
def test_validate_file_type_accepts_valid_values(value):
    _validate_file_type(value)


@pytest.mark.parametrize("value", ["", ".parquet", "csv", "PARQUET"])
def test_validate_file_type_rejects_invalid_values(value):
    with pytest.raises(TypeError, match="file_type must be a FileType"):
        _validate_file_type(value)


@pytest.mark.parametrize("value", [None, [], ["dapla"], ["on-prem", "data_2026"]])
def test_validate_folders_accepts_valid_values(value):
    _validate_folders(value)


def test_validate_file_type_rejects_non_string():
    with pytest.raises(TypeError):
        _validate_file_type(123)
