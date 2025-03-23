import os
import re
from pathlib import Path

from dapla_metadata.datasets.dapla_dataset_path_info import DaplaDatasetPathInfo

MISSING_BUCKET_NAME = "Bøttenavn"
MISSING_VERSION = "Filnavn mangler versjonsnummer ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#filnavn"
MISSING_PERIOD = "Filnavn mangler gyldighetsperiode ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#filnavn"
MISSING_SHORT_NAME = "Kortnavn for statistikk mangler"
MISSING_DATA_STATE = "Mappe for datatilstand mangler ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#obligatoriske-mapper"
MISSING_DATASET_SHORT_NAME = "Filnavn mangler beskrivelse."
NAME_STANDARD_SUCSESS = "Filene dine er i samsvar med SSB-navnestandarden"
NAME_STANDARD_VIOLATION = "Det er oppdaget brudd på SSB-navnestandard:"
INVALID_SYMBOLS = "Filnavn inneholder ulovlige tegn ref:"
PATH_IGNORED = "Mappen er ikke underlagt krav til navnestandard"
FILE_PATH_NOT_CONFIRMED = "Det var ikke mulig å bekrefte at filstien eksisterer. Validering ble utført uten å kunne bekrefte filens eksistens."
IGNORED_FOLDERS = [
    "temp",
    "oppdrag",
    "konfigurasjon",
    "logg",
    "tidsserier",
    "migrert",
]


class ValidationResult:
    """Result object for name standard validation."""

    def __init__(self) -> None:
        """Initialize the validatation result."""
        self.success: bool = True
        self.messages: list = []
        self.violations: list = []
        self.file_exists = None  # Will be set to True or False later
        self.file_check_status: str = (None,)

    def add_message(self, message: str) -> None:
        """Add message to list."""
        self.messages.append(message)

    def add_violation(self, violation: str) -> None:
        """Add violation to list."""
        self.violations.append(violation)
        self.success = False  # If there's any violation, success becomes False

    def set_file_check_status(self, status_message: str | None) -> None:
        """Set."""
        self.file_check_status = status_message
        self.add_message(status_message)

    def __str__(self) -> str:
        """Something."""
        if self.success:
            return f"Success: {', '.join(self.messages)}"
        return f"Violations: {', '.join(self.violations)}"


class NameStandardValidator:
    """Validator for ensuring file names adhere to naming standards."""

    INVALID_PATTERN = r"[^a-zA-Z0-9\./:_-]"

    IGNORED_DATA_STATE_FOLDER = "SOURCE_DATA"

    def __init__(
        self,
        file_path: str | os.PathLike[str] | None,
        bucket_name: Path | str | None,
    ) -> None:
        """Initialize the validator with file path information."""
        self.file_path = Path(file_path).resolve() if file_path else None
        self.bucket_name = bucket_name if bucket_name else None
        self.result: ValidationResult = ValidationResult()
        if self.file_path:
            self.path_info = DaplaDatasetPathInfo(str(file_path))

        if self.bucket_name:
            self.bucket_directory: Path | None = Path.cwd() / self.bucket_name
        else:
            self.bucket_directory = None

    @staticmethod
    def is_invalid_symbols(s: str) -> bool:
        """Return True if string contains illegal symbols.

        Examples:
            >>> NameStandardValidator.is_invalid_symbols("åregang-øre")
            True

            >>> NameStandardValidator.is_invalid_symbols("Azor89")
            False

            >>> NameStandardValidator.is_invalid_symbols("ssbÆ-dapla-example-data-produkt-prod/ledstill/oppdrag/skjema_p2018_p2020_v1")
            True

            >>> NameStandardValidator.is_invalid_symbols("ssb-dapla-example-data-produkt-prod/ledstill/oppdrag/skjema_p2018_p2020_v1")
            False
        """
        return bool(re.search(NameStandardValidator.INVALID_PATTERN, s.strip()))

    def validate(self) -> ValidationResult | str | list:
        """Check for naming standard violations.

        Returns:
            - A list of violation messages if any naming standards are violated.
            - A success message if no violations are found.
            - A message if the file path is in an ignored folder.
        """
        if self.path_info and self.file_path and self.file_path.exists():
            dataset_state = self.path_info.dataset_state
            checks = {
                MISSING_SHORT_NAME: self.path_info.statistic_short_name,
                MISSING_DATA_STATE: dataset_state,
                MISSING_PERIOD: self.path_info.contains_data_from,
                MISSING_DATASET_SHORT_NAME: self.path_info.dataset_short_name,
            }
            violations = [message for message, value in checks.items() if not value]
            if dataset_state == self.IGNORED_DATA_STATE_FOLDER:
                self.result.add_message(PATH_IGNORED)

                return self.result
            for i in IGNORED_FOLDERS:
                if i in self.file_path.as_posix().lower():
                    self.result.add_message(PATH_IGNORED)
                    return self.result

            if not dataset_state:
                self.result.add_message(MISSING_DATA_STATE)
                return self.result

            if self.is_invalid_symbols(self.file_path.as_posix()):
                violations.append(INVALID_SYMBOLS)
            self.result.violations = violations
            if not violations:
                self.result.add_message(NAME_STANDARD_SUCSESS)

            return self.result
        return "Filen eksisterer ikke"

    def validate_bucket(self) -> list:
        """Recursively validate all files in a directory."""
        result_list = []
        if self.bucket_directory:
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
        return ["Kan ikke validere bøtte navn"]
