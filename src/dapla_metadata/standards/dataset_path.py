"""Build complete or partial paths from validated dataset metadata."""

from __future__ import annotations

import re
from enum import StrEnum

from dapla_metadata._shared.constants import GS_PREFIX
from dapla_metadata._shared.dataset_naming import is_valid_dataset_short_name
from dapla_metadata._shared.period_parser import validate_period_range

_PATH_SEGMENT_PATTERN = re.compile(r"[A-Za-z0-9_-]+")
_VERSION_ERROR_MSG = "version must be a non-negative integer"


class FileType(StrEnum):
    """File types supported by the dataset path generator."""

    JSON = "json"
    CSV = "csv"
    XML = "xml"
    PARQUET = "parquet"


class DataState(StrEnum):
    """Data states supported by the dataset path generator.

    ``SOURCE_DATA`` is excluded: kildedata filenames are not covered by the
    naming standard that paths are generated from.
    """

    INPUT_DATA = "inndata"
    PROCESSED_DATA = "klargjorte-data"
    STATISTICS = "statistikk"
    OUTPUT_DATA = "utdata"


def create_dataset_path(  # noqa: PLR0913 - explicit path components are part of the public API
    *,
    bucket: str | None = None,
    product: str | None = None,
    data_state: DataState | None = None,
    short_description: str | None = None,
    period_from: str | None = None,
    period_to: str | None = None,
    version: int | None = None,
    file_type: FileType | None = None,
    folders: list[str] | None = None,
) -> str:
    """Build a complete or contiguous partial path from dataset metadata.

    The complete path has the form::

        gs://{bucket}/{product}/{data_state}/{folders...}/{short_description}_p{period_from}[_p{period_to}]_v{version}.{file_type}

    Any argument can be combined as long as they follow the correct order.

    A filename is atomic: ``short_description``, ``period_from``, ``version``,
    and ``file_type`` must either all be provided or all be omitted.
    ``period_to`` is optional, but can only be used as part of a complete
    filename.

    Callers should provide semantic values only. The function should add the
    ``gs://``, ``_p``, ``_v``, and ``.`` syntax itself. It should not access GCS,
    inspect the filesystem, or silently correct invalid input.

    Args:
        bucket: Optional bucket name, without the ``gs://`` prefix. It must be
            a non-empty single path segment: no slashes and no leading or
            trailing whitespace. Beyond that the name is included verbatim and
            is not validated against the full GCS naming rules, so callers are
            responsible for validating it when necessary. For example,
            ``"ssb-dapla-example-data-produkt-prod"``.
        product: Optional non-empty statistics-product or data-product short name. It
            may contain uppercase and lowercase letters, digits, ``-``, and
            ``_``. For example, ``"ledstill"`` or ``"ameld_data"``.
        data_state: An optional ``DataState`` enum member:
            ``DataState.INPUT_DATA``, ``DataState.PROCESSED_DATA``,
            ``DataState.STATISTICS``, or ``DataState.OUTPUT_DATA``. Do not
            pass a raw string.
        short_description: Optional non-empty dataset short description. It must
            contain only letters, digits, and hyphens, with no restriction on
            hyphen placement. Underscores, spaces, slashes, and periods are
            not accepted. For example, ``"varehandel"``,
            ``"grensehandel-imputert"``, or ``"-imputert--data-"``.
        period_from: The optional first period as a string. Do not include the ``p``
            prefix. Supported formats are:

            * year: ``YYYY`` — for example, ``"2019"``;
            * month: ``YYYY-MM`` — for example, ``"2022-10"``;
            * calendar date: ``YYYY-MM-DD`` — for example, ``"2022-01-24"``;
            * ISO week: ``YYYY-Www`` — for example, ``"2020-W15"``;
            * ISO ordinal date: ``YYYY-DDD`` — for example, ``"2022-015"``;
            * date and time: ``YYYY-MM-DDTHH-MM-SS.sss`` — for example,
              ``"2024-12-31T23-59-30.000"``;
            * SSB bimonthly period: ``YYYY-Bn``, where ``n`` is 1-6;
            * SSB quarterly period: ``YYYY-Qn``, where ``n`` is 1-4;
            * SSB four-month period: ``YYYY-Tn``, where ``n`` is 1-3;
            * SSB half-year period: ``YYYY-Hn``, where ``n`` is 1-2.

        period_to: An optional second period as a string, without the ``p``
            prefix. If supplied, it must use the same format as
            ``period_from`` and be in chronological order.
        version: An optional non-negative integer, such as ``0`` or ``3``. Do not
            include the ``v`` prefix.
        file_type: An optional ``FileType`` enum member: ``FileType.JSON``,
            ``FileType.CSV``, ``FileType.XML``, or ``FileType.PARQUET``. Do
            not pass a raw string or include the leading period.
        folders: ``None`` or a list of optional folder names below the
            product and data-state folders. Each folder must be non-empty and
            contain only letters, digits, ``-``, and ``_``. For example,
            ``["on-prem", "revidert_data"]``.

    Examples:
        Build a complete path:

        >>> create_dataset_path(
        ...     bucket="bucket",
        ...     product="ledstill",
        ...     data_state=DataState.OUTPUT_DATA,
        ...     short_description="varehandel",
        ...     period_from="2018-Q1",
        ...     version=1,
        ...     file_type=FileType.PARQUET,
        ... )
        'gs://bucket/ledstill/utdata/varehandel_p2018-Q1_v1.parquet'

        Build a partial path:

        >>> create_dataset_path(product="ledstill", data_state=DataState.INPUT_DATA)
        'ledstill/inndata'

        Build a filename:

        >>> create_dataset_path(short_description="befolkning", period_from="2025", version=0, file_type=FileType.JSON)
        'befolkning_p2025_v0.json'

        Build a path containing folders:

        >>> create_dataset_path(data_state=DataState.OUTPUT_DATA, folders=["publisert", "arkiv"])
        'utdata/publisert/arkiv'

        Build a filename containing a period range:

        >>> create_dataset_path(short_description="handel", period_from="2025-Q1", period_to="2025-Q4", version=2, file_type=FileType.CSV)
        'handel_p2025-Q1_p2025-Q4_v2.csv'

    Returns:
        A complete GCS path or contiguous relative path fragment.

    Raises:
        TypeError: If an argument has an invalid Python type.
        ValueError: If an argument does not satisfy the naming standard, the
            filename is incomplete, the path contains a hierarchy gap, or no
            path component is supplied.
    """
    _validate_supplied_values(
        bucket=bucket,
        product=product,
        data_state=data_state,
        short_description=short_description,
        period_from=period_from,
        period_to=period_to,
        version=version,
        file_type=file_type,
        folders=folders,
    )
    filename = _build_filename(
        short_description, period_from, period_to, version, file_type
    )
    _validate_contiguous_hierarchy(bucket, product, data_state, folders, filename)

    path_parts = [
        part
        for part in (bucket, product, data_state, *(folders or []), filename)
        if part is not None
    ]
    if not path_parts:
        msg = "At least one path component must be provided"
        raise ValueError(msg)

    path = "/".join(path_parts)
    return f"{GS_PREFIX}{path}" if bucket is not None else path


def _validate_supplied_values(  # noqa: PLR0913 - mirrors create_dataset_path components
    *,
    bucket: str | None,
    product: str | None,
    data_state: DataState | None,
    short_description: str | None,
    period_from: str | None,
    period_to: str | None,
    version: int | None,
    file_type: FileType | None,
    folders: list[str] | None,
) -> None:
    """Validate the type and format of each supplied path component."""
    _validate_bucket(bucket)
    _validate_product(product)
    _validate_data_state(data_state)
    _validate_short_description(short_description)
    _validate_periods(period_from, period_to)
    _validate_version(version)
    _validate_file_type(file_type)
    _validate_folders(folders)


def _build_filename(
    short_description: str | None,
    period_from: str | None,
    period_to: str | None,
    version: int | None,
    file_type: FileType | None,
) -> str | None:
    """Build a filename when all required filename components are supplied."""
    named_components = (
        ("short_description", short_description),
        ("period_from", period_from),
        ("version", version),
        ("file_type", file_type),
    )

    if period_to is None and all(value is None for _, value in named_components):
        return None

    if (
        short_description is None
        or period_from is None
        or version is None
        or file_type is None
    ):
        missing = [name for name, value in named_components if value is None]
        msg = (
            "short_description, period_from, version, and file_type must be "
            f"provided together; missing: {', '.join(missing)}"
        )
        raise ValueError(msg)

    period_section = f"_p{period_from}" + (
        f"_p{period_to}" if period_to is not None else ""
    )
    return f"{short_description}{period_section}_v{version}.{file_type.value}"


def _validate_contiguous_hierarchy(
    bucket: str | None,
    product: str | None,
    data_state: DataState | None,
    folders: list[str] | None,
    filename: str | None,
) -> None:
    """Reject gaps between supplied path hierarchy components."""
    has_folders = bool(folders)
    has_product_descendant = (
        data_state is not None or has_folders or filename is not None
    )
    if bucket is not None and product is None and has_product_descendant:
        msg = "product is required between bucket and later path components"
        raise ValueError(msg)
    if (
        (bucket is not None or product is not None)
        and data_state is None
        and (has_folders or filename is not None)
    ):
        msg = "data_state is required between product and later path components"
        raise ValueError(msg)


def _validate_bucket(bucket: object) -> None:
    """Validate a bucket name when one is supplied.

    Only checks that the value can form a single path segment. The name is not
    validated against the full GCS bucket naming rules.
    """
    if bucket is None:
        return
    if not isinstance(bucket, str):
        msg = "bucket must be a string"
        raise TypeError(msg)
    if not bucket or "/" in bucket or bucket.strip() != bucket:
        msg = "Invalid bucket name"
        raise ValueError(msg)


def _validate_product(product: object) -> None:
    """Validate a product path segment when one is supplied."""
    if product is None:
        return
    if not isinstance(product, str):
        msg = "product must be a string"
        raise TypeError(msg)
    if _PATH_SEGMENT_PATTERN.fullmatch(product) is None:
        msg = "Invalid product name"
        raise ValueError(msg)


def _validate_data_state(data_state: object) -> None:
    """Validate that a data state is a supported enum member when one is supplied."""
    if data_state is None:
        return
    if not isinstance(data_state, DataState):
        msg = "data_state must be a DataState"
        raise TypeError(msg)


def _validate_short_description(short_description: object) -> None:
    """Validate a dataset short description when one is supplied."""
    if short_description is None:
        return
    if not isinstance(short_description, str):
        msg = "short_description must be a string"
        raise TypeError(msg)
    if not is_valid_dataset_short_name(short_description):
        msg = "Invalid short description"
        raise ValueError(msg)


def _validate_periods(period_from: object = None, period_to: object = None) -> None:
    """Validate optional periods and their chronological order."""
    if not isinstance(period_from, str | None) or not isinstance(period_to, str | None):
        msg = "periods must be strings"
        raise TypeError(msg)
    if period_from is not None:
        validate_period_range(period_from, period_to)


def _validate_version(version: object) -> None:
    """Validate that a version is a non-negative integer when one is supplied."""
    if version is None:
        return
    if not isinstance(version, int) or isinstance(version, bool):
        raise TypeError(_VERSION_ERROR_MSG)
    if version < 0:
        raise ValueError(_VERSION_ERROR_MSG)


def _validate_file_type(file_type: object) -> None:
    """Validate that a file type is a supported enum member when one is supplied."""
    if file_type is None:
        return
    if not isinstance(file_type, FileType):
        msg = "file_type must be a FileType"
        raise TypeError(msg)


def _validate_folders(folders: list[str] | None) -> None:
    """Validate optional folder path segments."""
    if folders is None:
        return
    if not isinstance(folders, list) or any(
        not isinstance(folder, str) for folder in folders
    ):
        msg = "folders must be a list of strings or None"
        raise TypeError(msg)
    for folder in folders:
        if _PATH_SEGMENT_PATTERN.fullmatch(folder) is None:
            msg = f"Invalid folder name: {folder}"
            raise ValueError(msg)
