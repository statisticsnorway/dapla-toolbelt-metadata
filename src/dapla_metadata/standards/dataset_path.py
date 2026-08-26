# Copyright (c) 2026 Statistics Norway
"""Build complete GCS paths from validated dataset metadata."""

from __future__ import annotations

import re
from enum import StrEnum

from dapla_metadata._shared.dataset_naming import CANONICAL_DATA_STATE_NAMES
from dapla_metadata._shared.dataset_naming import is_valid_dataset_short_name
from dapla_metadata._shared.period_parser import validate_period_range
from dapla_metadata.datasets.utility.constants import GS_PREFIX

_BUCKET_PATTERN = re.compile(r"[a-z0-9][a-z0-9._-]*[a-z0-9]")
_PATH_SEGMENT_PATTERN = re.compile(r"[A-Za-z0-9_-]+")


class FileType(StrEnum):
    """File types supported by the dataset path generator."""

    JSON = "json"
    CSV = "csv"
    XML = "xml"
    PARQUET = "parquet"


def dataset_path(  # noqa: PLR0913 - explicit path components are part of the public API
    *,
    bucket: str,
    product: str,
    data_state: str,
    short_description: str,
    period_from: str,
    period_to: str | None = None,
    version: int,
    file_type: FileType,
    folders: list[str] | None = None,
) -> str:
    """Build a complete GCS path from semantic dataset metadata.

    The function validates all arguments and returns a path in the form::

        gs://{bucket}/{product}/{data_state}/{folders...}/{short_description}_p{period_from}[_p{period_to}]_v{version}.{file_type}

    When two periods are provided, both should be included in the filename::

        gs://{bucket}/{product}/{data_state}/{short_description}_p{from}_p{to}_v{version}.{file_type}

    Callers should provide semantic values only. The function should add the
    ``gs://``, ``_p``, ``_v``, and ``.`` syntax itself. It should not access GCS,
    inspect the filesystem, or silently correct invalid input.

    Args:
        bucket: GCS bucket name, without the ``gs://`` prefix. It must contain
            3-63 characters for a single-label bucket, or 3-222 characters for
            a dotted bucket, and use lowercase letters, digits, ``.``, ``-``,
            and ``_``. It must start and end with a letter or digit. For
            example, ``"ssb-dapla-example-data-produkt-prod"``.
        product: Non-empty statistics-product or data-product short name. It
            may contain uppercase and lowercase letters, digits, ``-``, and
            ``_``. For example, ``"ledstill"`` or ``"ameld_data"``.
        data_state: One of ``"inndata"``, ``"klargjorte-data"``,
            ``"statistikk"``, or ``"utdata"``.
        short_description: Non-empty dataset short description. It must use
            only letters and digits, with optional single hyphens between
            alphanumeric parts. Underscores, spaces, slashes, and periods are
            not accepted. For example, ``"varehandel"`` or
            ``"grensehandel-imputert"``.
        period_from: The first period as a string. Do not include the ``p``
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
        version: A non-negative integer, such as ``0`` or ``3``. Do not
            include the ``v`` prefix.
        file_type: A ``FileType`` enum member: ``FileType.JSON``,
            ``FileType.CSV``, ``FileType.XML``, or ``FileType.PARQUET``. Do
            not pass a raw string or include the leading period.
        folders: ``None`` or a list of optional folder names below the
            product and data-state folders. Each folder must be non-empty and
            contain only letters, digits, ``-``, and ``_``. For example,
            ``["on-prem", "revidert_data"]``.

    Example:
        ``dataset_path(bucket="bucket", product="ledstill",
        data_state="utdata", short_description="varehandel",
        period_from="2018-Q1", version=1, file_type=FileType.PARQUET)``
        returns ``"gs://bucket/ledstill/utdata/varehandel_p2018-Q1_v1.parquet"``.

    Returns:
        The complete GCS object path.

    Raises:
        TypeError: If an argument has an invalid Python type.
        ValueError: If an argument does not satisfy the naming standard.
    """
    _validate_bucket(bucket)
    _validate_product(product)
    _validate_data_state(data_state)
    _validate_short_description(short_description)
    _validate_periods(period_from, period_to)
    _validate_version(version)
    _validate_file_type(file_type)
    _validate_folders(folders)

    directory_parts = [bucket, product, data_state, *(folders or [])]
    period_section = f"_p{period_from}"
    if period_to is not None:
        period_section += f"_p{period_to}"
    filename = f"{short_description}{period_section}_v{version}.{file_type.value}"
    return f"{GS_PREFIX}{'/'.join(directory_parts)}/{filename}"


def _validate_bucket(bucket: str) -> None:
    if not isinstance(bucket, str):
        msg = "bucket must be a string"
        raise TypeError(msg)

    labels = bucket.split(".")
    maximum_length = 222 if len(labels) > 1 else 63
    if (
        not 3 <= len(bucket) <= maximum_length
        or _BUCKET_PATTERN.fullmatch(bucket) is None
        or any(not label or len(label) > 63 for label in labels)
    ):
        msg = "Invalid GCS bucket name"
        raise ValueError(msg)


def _validate_product(product: str) -> None:
    if not isinstance(product, str):
        msg = "product must be a string"
        raise TypeError(msg)
    if _PATH_SEGMENT_PATTERN.fullmatch(product) is None:
        msg = "Invalid product name"
        raise ValueError(msg)


def _validate_data_state(data_state: str) -> None:
    if not isinstance(data_state, str):
        msg = "data_state must be a string"
        raise TypeError(msg)
    if data_state not in CANONICAL_DATA_STATE_NAMES:
        msg = "Invalid data_state"
        raise ValueError(msg)


def _validate_short_description(short_description: str) -> None:
    if not isinstance(short_description, str):
        msg = "short_description must be a string"
        raise TypeError(msg)
    if not is_valid_dataset_short_name(short_description):
        msg = "Invalid short description"
        raise ValueError(msg)


def _validate_periods(period_from: str, period_to: str | None = None) -> None:
    if not isinstance(period_from, str) or (
        period_to is not None and not isinstance(period_to, str)
    ):
        msg = "periods must be strings"
        raise TypeError(msg)
    validate_period_range(period_from, period_to)


def _validate_version(version: int) -> None:
    if not isinstance(version, int) or isinstance(version, bool):
        msg = "version must be a non-negative integer"
        raise TypeError(msg)
    if version < 0:
        msg = "version must be a non-negative integer"
        raise ValueError(msg)


def _validate_file_type(file_type: FileType) -> None:
    if not isinstance(file_type, FileType):
        msg = "file_type must be a FileType"
        raise TypeError(msg)


def _validate_folders(folders: list[str] | None) -> None:
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
