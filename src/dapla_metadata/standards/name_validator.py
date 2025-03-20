import re
from pathlib import Path
from typing import ClassVar

from cloudpathlib import CloudPath

from dapla_metadata.datasets.dapla_dataset_path_info import DaplaDatasetPathInfo

MISSING_VERSION = "Filnavn mangler versjonsnummer ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#filnavn"
MISSING_PERIOD = "Filnavn mangler gyldighetsperiode ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#filnavn"
MISSING_SHORT_NAME = "Kortnavn for statistikk mangler"
MISSING_DATA_STATE = "Mappe for datatilstand mangler ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#obligatoriske-mapper"
MISSING_DATASET_SHORT_NAME = "Filnavn mangler beskrivelse."
NAME_STANDARD_SUCSESS = "Filene dine er i samsvar med SSB-navnestandarden"
INVALID_SYMBOLS = "Filnavn inneholder ulovlige tegn ref:"
PATH_IGNORED = "Mappen er ikke underlagt krav til navnestandard"
INVALID_PATTERN = r"[^a-zA-Z0-9\./:_-]"


def _is_invalid_symbols(s: str) -> bool:
    s = s.strip()
    return bool(re.search(INVALID_PATTERN, s))


class NameStandardValidator:
    """Validator for ensuring file names adhere to naming standards."""

    IGNORED_DATA_STATE_FOLDER = "SOURCE_DATA"

    IGNORED_FOLDERS: ClassVar[list[str]] = [
        "temp",
        "oppdrag",
        "konfigurasjon",
        "logg",
        "tidsserier",
        "migrert",
    ]

    def __init__(self, file_path: Path | CloudPath) -> None:
        """Initialize the validator with file path information."""
        self.file_path = str(file_path)
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
            MISSING_DATASET_SHORT_NAME: self.path_info.dataset_short_name,
        }

        violations = [message for message, value in checks.items() if not value]
        if dataset_state == self.IGNORED_DATA_STATE_FOLDER:
            return PATH_IGNORED
        for i in self.IGNORED_FOLDERS:
            if i in self.file_path.lower():
                return PATH_IGNORED
        if not dataset_state:
            return MISSING_DATA_STATE
        if _is_invalid_symbols(self.file_path):
            violations.append(INVALID_SYMBOLS)
        return violations if violations else NAME_STANDARD_SUCSESS
