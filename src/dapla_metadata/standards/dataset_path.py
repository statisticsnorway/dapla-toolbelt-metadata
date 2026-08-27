"""Build complete or partial paths from validated dataset metadata."""

from __future__ import annotations

import re
from enum import StrEnum
from typing import cast

from dapla_metadata._shared.constants import GS_PREFIX
from dapla_metadata._shared.dataset_naming import CANONICAL_DATA_STATE_NAMES
from dapla_metadata._shared.dataset_naming import is_valid_dataset_short_name
from dapla_metadata._shared.period_parser import validate_period_range

_PATH_SEGMENT_PATTERN = re.compile(r"[A-Za-z0-9_-]+")


class FileType(StrEnum):
    """File types supported by the dataset path generator."""

    JSON = "json"
    CSV = "csv"
    XML = "xml"
    PARQUET = "parquet"


def dataset_path(  # noqa: PLR0913 - explicit path components are part of the public API
    *,
    bucket: str | None = None,
    product: str | None = None,
    data_state: str | None = None,
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

    Any contiguous section can be returned, including a filename alone,
    ``data_state/folders.../filename``, or ``bucket/product``. Leading and
    trailing sections may be omitted, but supplied sections cannot have a gap.
    Optional folders do not create a gap. For example, ``product/filename`` is
    invalid because ``data_state`` is missing, while ``data_state/filename``
    is valid.

    A filename is atomic: ``short_description``, ``period_from``, ``version``,
    and ``file_type`` must either all be provided or all be omitted.
    ``period_to`` is optional, but can only be used as part of a complete
    filename.

    Callers should provide semantic values only. The function should add the
    ``gs://``, ``_p``, ``_v``, and ``.`` syntax itself. It should not access GCS,
    inspect the filesystem, or silently correct invalid input.

    Args:
        bucket: Optional bucket name, without the ``gs://`` prefix. The name is
            included verbatim and is not validated against GCS naming rules.
            Callers are responsible for validating it when necessary. For example,
            ``"ssb-dapla-example-data-produkt-prod"``.
        product: Optional non-empty statistics-product or data-product short name. It
            may contain uppercase and lowercase letters, digits, ``-``, and
            ``_``. For example, ``"ledstill"`` or ``"ameld_data"``.
        data_state: Optionally one of ``"inndata"``, ``"klargjorte-data"``,
            ``"statistikk"``, or ``"utdata"``.
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

        >>> dataset_path(
        ...     bucket="bucket",
        ...     product="ledstill",
        ...     data_state="utdata",
        ...     short_description="varehandel",
        ...     period_from="2018-Q1",
        ...     version=1,
        ...     file_type=FileType.PARQUET,
        ... )
        'gs://bucket/ledstill/utdata/varehandel_p2018-Q1_v1.parquet'

        Build a partial path:

        >>> dataset_path(product="ledstill", data_state="inndata")
        'ledstill/inndata'

        Build a filename:

        >>> dataset_path(short_description="befolkning", period_from="2025", version=0, file_type=FileType.JSON)
        'befolkning_p2025_v0.json'

        Build a path containing folders:

        >>> dataset_path(data_state="utdata", folders=["publisert", "arkiv"])
        'utdata/publisert/arkiv'

        Build a filename containing a period range:

        >>> dataset_path(short_description="handel", period_from="2025-Q1", period_to="2025-Q4", version=2, file_type=FileType.CSV)
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


def _validate_supplied_values(  # noqa: PLR0913 - mirrors dataset_path components
    *,
    bucket: str | None,
    product: str | None,
    data_state: str | None,
    short_description: str | None,
    period_from: str | None,
    period_to: str | None,
    version: int | None,
    file_type: FileType | None,
    folders: list[str] | None,
) -> None:
    """Validate the type and format of each supplied path component."""
    _validate_bucket(bucket)
    if product is not None:
        _validate_product(product)
    if data_state is not None:
        _validate_data_state(data_state)
    if short_description is not None:
        _validate_short_description(short_description)
    if period_from is not None:
        _validate_periods(period_from, period_to)
    else:
        _validate_period_to(period_to)
    if version is not None:
        _validate_version(version)
    if file_type is not None:
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
    required = {
        "short_description": short_description,
        "period_from": period_from,
        "version": version,
        "file_type": file_type,
    }

    if period_to is None and all(value is None for value in required.values()):
        return None

    missing = [name for name, value in required.items() if value is None]
    if missing:
        msg = (
            "short_description, period_from, version, and file_type must be "
            f"provided together; missing: {', '.join(missing)}"
        )
        raise ValueError(msg)

    short_description = cast("str", short_description)
    period_from = cast("str", period_from)
    version = cast("int", version)
    file_type = cast("FileType", file_type)

    period_section = (
        f"_p{period_from}_p{period_to}" if period_to is not None else f"_p{period_from}"
    )
    return f"{short_description}{period_section}_v{version}.{file_type.value}"


def _validate_contiguous_hierarchy(
    bucket: str | None,
    product: str | None,
    data_state: str | None,
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
    """Validate the type of a bucket when one is supplied."""
    if bucket is not None and not isinstance(bucket, str):
        msg = "bucket must be a string"
        raise TypeError(msg)


def _validate_product(product: object) -> None:
    """Validate a product path segment."""
    if not isinstance(product, str):
        msg = "product must be a string"
        raise TypeError(msg)
    if _PATH_SEGMENT_PATTERN.fullmatch(product) is None:
        msg = "Invalid product name"
        raise ValueError(msg)


def _validate_data_state(data_state: object) -> None:
    """Validate that a data state is canonical."""
    if not isinstance(data_state, str):
        msg = "data_state must be a string"
        raise TypeError(msg)
    if data_state not in CANONICAL_DATA_STATE_NAMES:
        msg = "Invalid data_state"
        raise ValueError(msg)


def _validate_short_description(short_description: object) -> None:
    """Validate a dataset short description."""
    if not isinstance(short_description, str):
        msg = "short_description must be a string"
        raise TypeError(msg)
    if not short_description or not is_valid_dataset_short_name(short_description):
        msg = "Invalid short description"
        raise ValueError(msg)


def _validate_periods(period_from: object, period_to: object = None) -> None:
    """Validate one period or an optional chronological period range."""
    if not isinstance(period_from, str) or (
        period_to is not None and not isinstance(period_to, str)
    ):
        msg = "periods must be strings"
        raise TypeError(msg)
    validate_period_range(period_from, period_to)


def _validate_period_to(period_to: object) -> None:
    """Validate an optional end period supplied without a start period."""
    if period_to is not None and not isinstance(period_to, str):
        msg = "periods must be strings"
        raise TypeError(msg)


def _validate_version(version: int) -> None:
    """Validate that a version is a non-negative integer."""
    if not isinstance(version, int) or isinstance(version, bool):
        msg = "version must be a non-negative integer"
        raise TypeError(msg)
    if version < 0:
        msg = "version must be a non-negative integer"
        raise ValueError(msg)


def _validate_file_type(file_type: object) -> None:
    """Validate that a file type is a supported enum member."""
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
