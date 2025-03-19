import os
import re

from dapla_metadata.datasets.dapla_dataset_path_info import DaplaDatasetPathInfo

MISSING_VERSION = "Filnavn mangler versjonsnummer ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#filnavn"
MISSING_PERIOD = "Filnavn mangler gyldighetsperiode ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#filnavn"
MISSING_SHORT_NAME = "Kortnavn for statistikk mangler"
MISSING_DATA_STATE = "Mappe for datatilstand mangler ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#obligatoriske-mapper"
NAME_STANDARD_SUCSESS = "Filene dine er i samsvar med SSB-navnestandarden"
PATH_IGNORED = "Mappen er ikke underlagt krav til navnestandard"
VALID_PATTERN = r"^[a-zA-Z0-9_-]+$"


def _is_valid_symbols(s: str) -> bool:
    return bool(re.match(VALID_PATTERN, s))


class NameStandardValidator:
    """Validator for ensuring file names adhere to naming standards."""

    IGNORED_DATA_STATE_FOLDER = "SOURCE_DATA"
    IGNORED_FOLDER = "temp"

    def __init__(self, file_path: str | os.PathLike[str]) -> None:
        """Initialize the validator with file path information."""
        self.file_path = file_path
        self.path_info = DaplaDatasetPathInfo(file_path)

    @property
    def validate(self) -> str | list:
        """Check for naming standard violations.

        Returns:
            - A list of violation messages if any naming standards are violated.
            - A success message if no violations are found.
            - A message if the file path is in an ignored folder.
        """
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
        if not _is_valid_symbols(self.file_path):
            return ""
        return violations if violations else NAME_STANDARD_SUCSESS
