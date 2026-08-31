import re
from datetime import date

import pytest
from hypothesis import given
from hypothesis import strategies as st

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

ASCII_LOWER_AND_DIGITS = "abcdefghijklmnopqrstuvwxyz0123456789"
ASCII_LETTERS_AND_DIGITS = (
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
)

bucket_names = st.text(
    alphabet=ASCII_LETTERS_AND_DIGITS + "_-.",
    min_size=1,
    max_size=100,
)

valid_product_names = st.text(
    alphabet=ASCII_LETTERS_AND_DIGITS + "_-",
    min_size=1,
    max_size=40,
)

valid_name_segments = st.text(
    alphabet=ASCII_LETTERS_AND_DIGITS,
    min_size=1,
    max_size=20,
)
valid_dataset_names = st.lists(
    valid_name_segments,
    min_size=1,
    max_size=4,
).map("-".join)
valid_folders = st.lists(
    st.text(alphabet=ASCII_LETTERS_AND_DIGITS + "_-", min_size=1, max_size=20),
    max_size=4,
)

valid_year_periods = st.integers(min_value=1900, max_value=2100).map(str)
valid_month_periods = st.tuples(
    st.integers(min_value=1900, max_value=2100),
    st.integers(min_value=1, max_value=12),
).map(lambda value: f"{value[0]:04d}-{value[1]:02d}")
valid_day_periods = st.dates(
    min_value=date(1900, 1, 1),
    max_value=date(2100, 12, 31),
).map(str)
valid_week_periods = st.dates(
    min_value=date(1900, 1, 1),
    max_value=date(2100, 12, 31),
).map(lambda value: f"{value.isocalendar().year:04d}-W{value.isocalendar().week:02d}")
valid_ordinal_periods = st.dates(
    min_value=date(1900, 1, 1),
    max_value=date(2100, 12, 31),
).map(lambda value: value.strftime("%Y-%j"))
valid_datetimes = st.tuples(
    st.dates(min_value=date(1900, 1, 1), max_value=date(2100, 12, 31)),
    st.times(),
)
valid_datetime_periods = valid_datetimes.map(
    lambda value: f"{value[0]}T{value[1]:%H-%M-%S}.{value[1].microsecond // 1000:03d}"
)
valid_ssb_periods = st.one_of(
    st.tuples(st.integers(1900, 2100), st.integers(1, 6)).map(
        lambda value: f"{value[0]:04d}-B{value[1]}"
    ),
    st.tuples(st.integers(1900, 2100), st.integers(1, 4)).map(
        lambda value: f"{value[0]:04d}-Q{value[1]}"
    ),
    st.tuples(st.integers(1900, 2100), st.integers(1, 3)).map(
        lambda value: f"{value[0]:04d}-T{value[1]}"
    ),
    st.tuples(st.integers(1900, 2100), st.integers(1, 2)).map(
        lambda value: f"{value[0]:04d}-H{value[1]}"
    ),
)
valid_single_periods = st.one_of(
    valid_year_periods,
    valid_month_periods,
    valid_day_periods,
    valid_week_periods,
    valid_ordinal_periods,
    valid_datetime_periods,
    valid_ssb_periods,
)


@given(
    bucket=bucket_names,
    product=valid_product_names,
    data_state=st.sampled_from(DataState),
    short_description=valid_dataset_names,
    period=valid_single_periods,
    version=st.integers(min_value=0, max_value=10**9),
    folders=valid_folders,
)
def test_dataset_path_preserves_valid_semantic_values(
    bucket,
    product,
    data_state,
    short_description,
    period,
    version,
    folders,
):
    result = dataset_path(
        bucket=bucket,
        product=product,
        data_state=data_state,
        short_description=short_description,
        period_from=period,
        version=version,
        file_type=FileType.PARQUET,
        folders=folders,
    )

    folder_sections = "" if not folders else "/".join(folders) + "/"
    assert result == (
        f"gs://{bucket}/{product}/{data_state.value}/{folder_sections}"
        f"{short_description}_p{period}_v{version}.parquet"
    )


@given(
    first=st.integers(min_value=1900, max_value=2100),
    second=st.integers(min_value=1900, max_value=2100),
)
def test_dataset_path_orders_two_period_markers_without_modifying_values(first, second):
    period_from, period_until = sorted((first, second))

    result = dataset_path(
        bucket="bucket",
        product="product",
        data_state=DataState.OUTPUT_DATA,
        short_description="dataset",
        period_from=str(period_from),
        period_to=str(period_until),
        version=1,
        file_type=FileType.PARQUET,
    )

    assert result.endswith(f"dataset_p{period_from}_p{period_until}_v1.parquet")


@given(valid_product_names)
def test_validate_product_accepts_generated_valid_names(value):
    _validate_product(value)


@given(
    st.text(min_size=1, max_size=30).filter(
        lambda value: re.search(r"[^A-Za-z0-9_-]", value)
    )
)
def test_validate_product_rejects_generated_invalid_characters(value):
    with pytest.raises(ValueError, match="Invalid product name"):
        _validate_product(value)


@given(st.sampled_from(DataState))
def test_validate_data_state_accepts_only_generated_canonical_states(value):
    _validate_data_state(value)


@given(st.text(max_size=30))
def test_validate_data_state_rejects_generated_noncanonical_states(value):
    with pytest.raises(TypeError, match="data_state must be a DataState"):
        _validate_data_state(value)


@given(valid_dataset_names)
def test_validate_short_description_accepts_generated_valid_values(value):
    _validate_short_description(value)


@given(
    st.text(max_size=30).filter(
        lambda value: not value or re.search(r"[^A-Za-z0-9\-]", value)
    )
)
def test_validate_short_description_rejects_generated_invalid_values(value):
    with pytest.raises(ValueError, match="Invalid short description"):
        _validate_short_description(value)


@given(valid_single_periods)
def test_validate_periods_accepts_generated_supported_periods(value):
    _validate_periods(value)


@given(valid_single_periods)
def test_validate_periods_rejects_generated_prefixed_periods(value):
    with pytest.raises(ValueError, match="must not include the 'p' prefix"):
        _validate_periods(f"p{value}")


@given(st.integers(min_value=0))
def test_validate_version_accepts_generated_non_negative_integers(value):
    _validate_version(value)


@given(st.integers(max_value=-1))
def test_validate_version_rejects_generated_negative_integers(value):
    with pytest.raises(ValueError, match="version must be a non-negative integer"):
        _validate_version(value)


@given(st.text(max_size=30).filter(lambda value: value != "parquet"))
def test_validate_file_type_rejects_every_generated_unsupported_type(value):
    with pytest.raises(TypeError, match="file_type must be a FileType"):
        _validate_file_type(value)


@given(valid_folders)
def test_validate_folders_accepts_generated_valid_folders(value):
    _validate_folders(value)
