import os

from dapla_metadata.datasets.dapla_dataset_path_info import DaplaDatasetPathInfo

# ref
MISSING_VERSION = "Filnavn mangler versjonsnummer"
MISSING_PERIOD = "Filnavn mangler gyldighetsperiode"
MISSING_SHORT_NAME = "Kortnavn for statistikk mangler"
MISSING_DATA_STATE = "Mappe for datatilstand mangler"
NAME_STANDARD_SUCSESS = "Filene dine er i samsvar med SSB-navnestandarden"


class NameStandardValidator:
    """violating name standards."""

    def __init__(self, file_path_info: str | os.PathLike[str]) -> None:
        """Set."""
        self.file_path_info = DaplaDatasetPathInfo(file_path_info)

    @property
    def validate(self) -> str | list:
        """If None."""
        checks = {
            MISSING_DATA_STATE: self.file_path_info.dataset_state,
            MISSING_SHORT_NAME: self.file_path_info.statistic_short_name,
            MISSING_PERIOD: self.file_path_info.contains_data_from,
            MISSING_VERSION: self.file_path_info.dataset_version,
        }

        # dict header
        violations = [message for message, value in checks.items() if not value]

        return violations if violations else "Your files comply to SSB naming standard"
