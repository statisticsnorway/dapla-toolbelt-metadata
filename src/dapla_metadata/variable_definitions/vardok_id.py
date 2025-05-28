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
    """A Vardok id.

    - Provides access to the Vardok id filed.
    - Provides methods allowing maintenance for nicer output of the Vardok id.

    Args:
        VardokIdResponse: The Pydantic model superclass, representing a Vardok id response.
    """

    _file_path: Path | None = PrivateAttr(None)

    model_config = ConfigDict(use_enum_values=True, str_strip_whitespace=True)

    @staticmethod
    def from_model(
        model: VardokIdResponse,
    ) -> "VardokId":
        """Create a VariableDefinition instance from a CompleteResponse."""
        return VardokId.model_construct(**model.model_dump())

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
