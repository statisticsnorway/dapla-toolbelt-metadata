import os

from dapla_metadata.datasets.dapla_dataset_path_info import DaplaDatasetPathInfo


class NameStandardValidator:
    """violating name standards."""

    def __init__(self, file_path_info: str | os.PathLike[str]) -> None:
        """Set."""
        self.file_path_info = DaplaDatasetPathInfo(file_path_info)

    @property
    def validate(self) -> str | list:
        """If None."""
        checks = {
            "Missing folder for data": self.file_path_info.dataset_state,
            "Missing folder short name": self.file_path_info.statistic_short_name,
            "Missing valid from": self.file_path_info.contains_data_from,
            "Missing dataset version": self.file_path_info.dataset_version,
        }

        violations = [message for message, value in checks.items() if not value]

        return violations if violations else "Your files comply to SSB naming standard"
