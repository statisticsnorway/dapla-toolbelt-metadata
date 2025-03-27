import logging
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
from dapla_metadata.standards.utils.constants import PATH_IGNORED

logger = logging.getLogger(__name__)


class ValidationResult:
    """Result object for name standard validation."""

    def __init__(
        self,
        success: bool = True,
    ) -> None:
        """Initialize the validatation result."""
        self.success: bool = success
        self.file_path: str | None = None
        self.messages: list[str] = []
        self.violations: list[str] = []

    def add_message(self, message: str) -> None:
        """Add message to list."""
        if message not in self.messages:
            self.messages.append(message)

    def add_violation(self, violation: str) -> None:
        """Add violation to list."""
        if violation not in self.violations:
            self.violations.append(violation)
        if self.success:
            self.success = False

    def __repr__(self) -> str:
        """Representation for debugging."""
        return f"ValidationResult(success={self.success}, file_path={self.file_path}, messages={self.messages}, violations={self.violations})"

    def to_dict(self) -> dict:
        """Return result as a dictionary."""
        return {
            "success": self.success,
            "file_path": self.file_path,
            "messages": self.messages,
            "violations": self.violations,
        }


class BucketNameValidator:
    """Validator for ensuring file names from bucket name adhere to naming standard."""

    def __init__(
        self,
        bucket_name: Path | str,
    ) -> None:
        """Initialize the validator with file path information."""
        self.bucket_name = bucket_name
        self.result: ValidationResult = ValidationResult()

        root = Path("/buckets")
        self.bucket_directory: Path = root / self.bucket_name

    def validate(self) -> list[ValidationResult]:
        """Recursively validate all files in a directory."""
        validation_results = []
        processed_files = set()

        if not self.bucket_name or not self.bucket_directory.exists():
            self.result.file_path = self.bucket_directory
            self.result.add_message(BUCKET_NAME_UNKNOWN)
            return validation_results.append(self.result)

        for entry in self.bucket_directory.rglob("*"):
            if entry.is_file():
                msg = f"Validating file: {entry}"
                logger.debug(msg)

                if entry not in processed_files:
                    validator = NameStandardValidator(
                        file_path=entry,
                    )
                    file_result = validator.validate()
                    validation_results.append(file_result)
                    processed_files.add(entry)

                else:
                    msg = f"Skipping already validated file: {entry}"
                    logger.debug(msg)

            elif entry.is_dir():
                continue

        return validation_results


class NameStandardValidator:
    """Validator for ensuring file names adhere to naming standards."""

    INVALID_PATTERN = r"[^a-zA-Z0-9\./:_-]"

    IGNORED_DATA_STATE_FOLDER = "SOURCE_DATA"

    def __init__(
        self,
        file_path: str | os.PathLike[str],
    ) -> None:
        """Initialize the validator with file path information."""
        self.file_path = Path(file_path).resolve()
        self.result: ValidationResult = ValidationResult()
        self.path_info = DaplaDatasetPathInfo(str(file_path))

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
            self.result.add_message(
                FILE_PATH_NOT_CONFIRMED,
            )

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
            folder in self.file_path.as_posix().lower()
            for folder in IGNORED_FOLDERS
            if self.file_path is not None
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

        if self.file_path is not None and self.is_invalid_symbols(
            self.file_path.as_posix(),
        ):
            violations.append(INVALID_SYMBOLS)

        for violation in violations:
            self.result.add_violation(violation)

    def validate(self) -> ValidationResult:
        """Check for naming standard violations.

        Returns:
            A ValidationResult object containing messages and violations
        """
        self.result.file_path = str(self.file_path)

        if self.path_info and not self.file_path:
            return self.result

        if self._handle_ignored_folders():
            return self.result

        self._check_path_existence()
        self._check_violations()

        if self.result.success:
            self.result.add_message(
                NAME_STANDARD_SUCSESS,
            )
        return self.result
