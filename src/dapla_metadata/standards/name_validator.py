import os
import re
from pathlib import Path

from dapla_metadata.datasets.dapla_dataset_path_info import DaplaDatasetPathInfo
from dapla_metadata.standards.utils.constants import BUCKET_NAME_UNKNOWN
from dapla_metadata.standards.utils.constants import FILE_PATH_NOT_CONFIRMED
from dapla_metadata.standards.utils.constants import IGNORED_FOLDERS
from dapla_metadata.standards.utils.constants import INVALID_SYMBOLS
from dapla_metadata.standards.utils.constants import MISSING_DATA_STATE
from dapla_metadata.standards.utils.constants import MISSING_DATASET_SHORT_NAME
from dapla_metadata.standards.utils.constants import MISSING_PERIOD
from dapla_metadata.standards.utils.constants import MISSING_SHORT_NAME
from dapla_metadata.standards.utils.constants import NAME_STANDARD_SUCSESS
from dapla_metadata.standards.utils.constants import NAME_STANDARD_VIOLATION
from dapla_metadata.standards.utils.constants import PATH_IGNORED
from dapla_metadata.standards.utils.constants import SUCCESS


class ValidationResult:
    """Result object for name standard validation."""

    def __init__(self) -> None:
        """Initialize the validatation result."""
        self.success: bool = True
        self.messages: list[str] = []
        self.violations: list[str] = []

    def add_message(self, message: str) -> None:
        """Add message to list."""
        self.messages.append(message)

    def add_violation(self, violation: str) -> None:
        """Add violation to list."""
        self.violations.append(violation)
        if self.success:
            self.success = False

    def merge_result(self, other: "ValidationResult") -> None:
        """Merge another ValidationResult into this one.

        This method appends the messages and violations from another `ValidationResult`
        to the current instance. If the other result has a failure (success is False),
        the current instance's success status will be updated to False.

        Args:
            other (ValidationResult): Another validation result to merge into this one.
        """
        self.messages.extend(other.messages)
        self.violations.extend(other.violations)
        if not other.success:
            self.success = False

    def __str__(self) -> str:
        """String result of validation."""
        if self.success:
            return f"{SUCCESS}: {', '.join(self.messages)}"
        return f"{NAME_STANDARD_VIOLATION}: {', '.join(self.violations)}"

    def __repr__(self) -> str:
        """Representation for debugging."""
        return f"ValidationResult(success={self.success}, messages={self.messages}, violations={self.violations})"

    def as_dict(self) -> dict:
        """Return result as a dictionary."""
        return {
            "success": self.success,
            "messages": self.messages,
            "violations": self.violations,
        }


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

    def _check_path_existence(self) -> None:
        """Check if the file path exists and add a message if not."""
        if self.file_path and not self.file_path.exists():
            self.result.add_message(FILE_PATH_NOT_CONFIRMED)

    def _handle_ignored_folders(
        self,
    ) -> bool:
        """Check dataset state and handle ignored cases.

        Returns:
            bool: True if validation should stop due to ignored dataset state.
        """
        dataset_state = self.path_info.dataset_state
        if dataset_state == self.IGNORED_DATA_STATE_FOLDER:
            self.result.add_message(PATH_IGNORED)
            return True

        if any(
            folder in self.file_path.as_posix().lower() for folder in IGNORED_FOLDERS
        ):
            self.result.add_message(PATH_IGNORED)
            return True

        return False

    def _check_violations(
        self,
    ) -> None:
        """Check for missing attributes and invalid symbols."""
        checks = {
            MISSING_SHORT_NAME: self.path_info.statistic_short_name,
            MISSING_DATA_STATE: self.path_info.dataset_state,
            MISSING_PERIOD: self.path_info.contains_data_from,
            MISSING_DATASET_SHORT_NAME: self.path_info.dataset_short_name,
        }

        violations = [message for message, value in checks.items() if not value]

        if self.is_invalid_symbols(self.file_path.as_posix()):
            violations.append(INVALID_SYMBOLS)

        for violation in violations:
            self.result.add_violation(violation)

    def validate(self) -> ValidationResult:
        """Check for naming standard violations.

        Returns:
            A ValidationResult object containing messages and violations
        """
        self._check_path_existence()
        if self.path_info and not self.file_path:
            return self.result

        if self._handle_ignored_folders():
            return self.result

        self._check_violations()

        if self.result.success:
            self.result.add_message(NAME_STANDARD_SUCSESS)

        return self.result

    def validate_bucket(self) -> ValidationResult:
        """Recursively validate all files in a directory."""
        final_result = ValidationResult()

        if self.bucket_directory and not self.bucket_directory.exists():
            final_result.add_message(BUCKET_NAME_UNKNOWN)
            return final_result

        for entry in os.scandir(self.bucket_directory):
            if entry.is_file():
                result = NameStandardValidator(
                    file_path=entry.path,
                    bucket_name=self.bucket_name,
                ).validate()
                final_result.merge_result(result)
            elif entry.is_dir():
                sub_result = NameStandardValidator(
                    file_path=None,
                    bucket_name=entry.path,
                ).validate_bucket()
                final_result.merge_result(sub_result)
        return final_result
