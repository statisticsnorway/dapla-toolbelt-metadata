import os
import re
from pathlib import Path

from dapla_metadata.datasets.dapla_dataset_path_info import DaplaDatasetPathInfo

MISSING_VERSION = "Filnavn mangler versjonsnummer ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#filnavn"
MISSING_PERIOD = "Filnavn mangler gyldighetsperiode ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#filnavn"
MISSING_SHORT_NAME = "Kortnavn for statistikk mangler"
MISSING_DATA_STATE = "Mappe for datatilstand mangler ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#obligatoriske-mapper"
NAME_STANDARD_SUCSESS = "Filene dine er i samsvar med SSB-navnestandarden"
INVALID_SYMBOLS = "Filnavn inneholder ulovlige tegn ref:"
PATH_IGNORED = "Mappen er ikke underlagt krav til navnestandard"
INVALID_PATTERN = r"[^a-zA-Z0-9\./:_-]"


def _is_invalid_symbols(s: str) -> bool:
    s = s.strip()
    return bool(re.search(INVALID_PATTERN, s))


def _is_bucket(file_path: str):
    """Check if the path is just a bucket name.

    Returns:
        True if the path bucket name, False otherwise.
    """
    file_path = file_path.rstrip("/")
    if file_path.startswith("gs://"):
        path_parts = Path(file_path.removeprefix("gs://")).parts
        return len(path_parts) == 1

    if file_path.startswith("buckets/"):
        path_parts = file_path.split("/")
        return len(path_parts) == 2

    return False


def _is_directory(bucket_name: str) -> bool:
    """Check if the given bucket name exists as a directory.

    Returns:
        True if the directory exists, False otherwise.
    """
    bucket_name = Path(bucket_name)
    return bucket_name.is_dir()


class NameStandardValidator:
    """Validator for ensuring file names adhere to naming standards."""

    IGNORED_DATA_STATE_FOLDER = "SOURCE_DATA"
    IGNORED_FOLDER = "temp"

    def __init__(self, file_path: str | os.PathLike[str]) -> None:
        """Initialize the validator with file path information."""
        self.file_path = file_path
        self.is_bucket = _is_bucket(self.file_path)
        self.path_info = DaplaDatasetPathInfo(file_path) if not self.is_bucket else None
        parts = (
            file_path.split("/")
            if file_path is not None and self.is_bucket is not None
            else None
        )
        self.bucket_name = parts[1] if parts is not None and len(parts) > 1 else None

    @property
    def validate(self) -> str | list:
        """Check for naming standard violations.

        Returns:
            - A list of violation messages if any naming standards are violated.
            - A success message if no violations are found.
            - A message if the file path is in an ignored folder.
        """
        if not self.is_bucket:
            dataset_state = self.path_info.dataset_state
            checks = {
                MISSING_DATA_STATE: dataset_state,
                MISSING_SHORT_NAME: self.path_info.statistic_short_name,
                MISSING_PERIOD: self.path_info.contains_data_from,
                MISSING_VERSION: self.path_info.dataset_version,
            }

            violations = [message for message, value in checks.items() if not value]
            if (
                dataset_state == self.IGNORED_DATA_STATE_FOLDER
                or self.IGNORED_FOLDER in self.file_path
            ):
                return PATH_IGNORED
            if _is_invalid_symbols(self.file_path):
                violations.append(INVALID_SYMBOLS)
            return violations if violations else NAME_STANDARD_SUCSESS
        if self.is_bucket:
            if not _is_directory(self.file_path):
                msg = "Not at directory"
                raise NotADirectoryError(msg)
            return "Something"
        return None
