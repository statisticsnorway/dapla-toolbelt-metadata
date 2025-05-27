import logging
from io import StringIO
from pathlib import Path

import ruamel.yaml
from pydantic import ConfigDict
from pydantic import PrivateAttr

from dapla_metadata.variable_definitions._generated.vardef_client.models.vardok_id_response import (
    VardokIdResponse,
)
from dapla_metadata.variable_definitions._utils.files import configure_yaml
from dapla_metadata.variable_definitions._utils.files import pre_process_data

logger = logging.getLogger(__name__)


class VardokId(VardokIdResponse):
    """A Variable Definition.

    - Provides access to the fields of the specific Variable Definition.
    - Provides methods to access Patches and Validity Periods of this Variable Definition.
    - Provides methods allowing maintenance of this Variable Definition.

    Args:
        CompleteResponse: The Pydantic model superclass, representing a Variable Definition.
    """

    _file_path: Path | None = PrivateAttr(None)

    model_config = ConfigDict(use_enum_values=True, str_strip_whitespace=True)

    def get_file_path(self) -> Path | None:
        """Get the file path where the variable definition has been written to for editing."""
        return self._file_path

    def set_file_path(self, file_path: Path | None) -> None:
        """Set the file path where the variable definition has been written to for editing."""
        self._file_path = file_path

    @staticmethod
    def from_model(
        model: VardokIdResponse,
    ) -> "VardokId":
        """Create a VariableDefinition instance from a CompleteResponse."""
        return VardokId.model_construct(**model.model_dump())

    def to_dict(self) -> dict:
        """Return as dictionary."""
        return super().to_dict()

    def __str__(self) -> str:
        """Format as indented YAML."""
        return self._convert_to_yaml_output()

    def __repr__(self) -> str:
        """Format as indented YAML."""
        return self._convert_to_yaml_output()

    def _convert_to_yaml_output(self) -> str:
        stream = StringIO()
        with ruamel.yaml.YAML(output=stream) as yaml:
            configure_yaml(yaml)
            data = self.model_dump(
                mode="json",
                serialize_as_any=True,
                warnings="error",
            )
            yaml.dump(pre_process_data(data))
        return stream.getvalue()
