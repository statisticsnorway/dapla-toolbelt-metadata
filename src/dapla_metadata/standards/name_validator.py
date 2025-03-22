import os
import re
from pathlib import Path

from cloudpathlib import CloudPath

from dapla_metadata.datasets.dapla_dataset_path_info import DaplaDatasetPathInfo

MISSING_BUCKET_NAME = "Bøttenavn"
MISSING_VERSION = "Filnavn mangler versjonsnummer ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#filnavn"
MISSING_PERIOD = "Filnavn mangler gyldighetsperiode ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#filnavn"
MISSING_SHORT_NAME = "Kortnavn for statistikk mangler"
MISSING_DATA_STATE = "Mappe for datatilstand mangler ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#obligatoriske-mapper"
MISSING_DATASET_SHORT_NAME = "Filnavn mangler beskrivelse."
NAME_STANDARD_SUCSESS = "Filene dine er i samsvar med SSB-navnestandarden"
INVALID_SYMBOLS = "Filnavn inneholder ulovlige tegn ref:"
PATH_IGNORED = "Mappen er ikke underlagt krav til navnestandard"
IGNORED_FOLDERS = [
    "temp",
    "oppdrag",
    "konfigurasjon",
    "logg",
    "tidsserier",
    "migrert",
]


class NameStandardValidator:
    """Validator for ensuring file names adhere to naming standards."""

    INVALID_PATTERN = r"[^a-zA-Z0-9\./:_-]"

    IGNORED_DATA_STATE_FOLDER = "SOURCE_DATA"

    def __init__(
        self,
        file_path: Path | CloudPath | None,
        bucket_name: Path | str | None,
    ) -> None:
        """Initialize the validator with file path information."""
        self.file_path = Path(file_path).resolve() if file_path else None
        self.bucket_name = bucket_name if bucket_name else None
        self.path_info = DaplaDatasetPathInfo(file_path) if self.file_path else None

        if self.bucket_name:
            self.bucket_directory = Path.cwd() / self.bucket_name
        else:
            self.bucket_directory = None

    @staticmethod
    def is_invalid_symbols(s: str) -> bool:
        """Return True if string contains illegal symbols."""
        return bool(re.search(NameStandardValidator.INVALID_PATTERN, s.strip()))

    def validate(self) -> str | list:
        """Check for naming standard violations.

        Returns:
            - A list of violation messages if any naming standards are violated.
            - A success message if no violations are found.
            - A message if the file path is in an ignored folder.
        """
        if self.path_info and self.file_path.exists():
            dataset_state = self.path_info.dataset_state
            checks = {
                MISSING_SHORT_NAME: self.path_info.statistic_short_name,
                MISSING_DATA_STATE: dataset_state,
                MISSING_PERIOD: self.path_info.contains_data_from,
                MISSING_DATASET_SHORT_NAME: self.path_info.dataset_short_name,
            }
            violations = [message for message, value in checks.items() if not value]
            if dataset_state == self.IGNORED_DATA_STATE_FOLDER:
                return PATH_IGNORED
            for i in IGNORED_FOLDERS:
                if i in self.file_path.as_posix().lower():
                    return PATH_IGNORED
            if not dataset_state:
                return MISSING_DATA_STATE
            if self.is_invalid_symbols(self.file_path.as_posix()):
                violations.append(INVALID_SYMBOLS)
            return violations if violations else NAME_STANDARD_SUCSESS
        return "Filen eksisterer ikke"

    def validate_bucket(self) -> list | str:
        """Recursively validate all files in a directory."""
        result_list = []
        for entry in os.scandir(self.bucket_directory):
            if entry.is_file():
                file_path = entry.path
                validator = NameStandardValidator(
                    file_path=file_path,
                    bucket_name=self.bucket_name,
                )
                result = validator.validate()
                result_list.append((file_path, result))
            elif entry.is_dir():
                sub_validator = NameStandardValidator(
                    file_path=None,
                    bucket_name=entry.path,
                )
                result_list.extend(sub_validator.validate_bucket())
        return result_list
