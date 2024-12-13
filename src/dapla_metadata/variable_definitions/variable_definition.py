from dapla_metadata.variable_definitions._client import VardefClient
from dapla_metadata.variable_definitions.generated.vardef_client.api.patches_api import (
    PatchesApi,
)
from dapla_metadata.variable_definitions.generated.vardef_client.api.validity_periods_api import (
    ValidityPeriodsApi,
)
from dapla_metadata.variable_definitions.generated.vardef_client.api.variable_definitions_api import (
    VariableDefinitionsApi,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.complete_response import (
    CompleteResponse,
)


class VariableDefinition(CompleteResponse):
    """A Variable Definition.

    - Provides access to the fields of the specific Variable Definition.
    - Provides methods to access Patches and Validity Periods of this Variable Definition.
    - Provides methods allowing maintenance of this Variable Definition.

    Args:
        CompleteResponse: The Pydantic model superclass, representing a Variable Definition.
    """

    @staticmethod
    def from_complete_response(
        complete_response: CompleteResponse,
    ) -> "VariableDefinition":
        """Create a VariableDefinition instance from a CompleteResponse."""
        return VariableDefinition.model_construct(**complete_response.model_dump())

    def list_validity_periods(self) -> list[CompleteResponse]:
        """List all Validity Periods for this Variable Definition."""
        return ValidityPeriodsApi(VardefClient.get_client()).list_validity_periods(
            variable_definition_id=self.id,
        )

    def list_patches(self) -> list[CompleteResponse]:
        """List all Patches for this Variable Definition."""
        return PatchesApi(VardefClient.get_client()).list_patches(
            variable_definition_id=self.id,
        )

    def get_patch(self, patch_id: int) -> CompleteResponse:
        """Get a single Patch by ID.

        Args:
            patch_id (int): The ID of the patch.

        Returns:
            CompleteResponse: The desired patch.
        """
        return PatchesApi(VardefClient.get_client()).get_patch(
            variable_definition_id=self.id,
            patch_id=patch_id,
        )

    @staticmethod
    def get_id_from_short_name(short_name: str) -> str:
        """Return id for variable definition based on short name.

        Args:
            short_name (str): The short name for one saved variable definition
        Returns:
            str: The id of the saved variable definition
        """
        variable = VariableDefinitionsApi(
            VardefClient.get_client(),
        ).list_variable_definitions()
        var_id = [var.id for var in variable if var.short_name == short_name]
        return var_id[0]
