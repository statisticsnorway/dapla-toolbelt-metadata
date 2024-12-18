from dapla_metadata.variable_definitions._client import VardefClient
from dapla_metadata.variable_definitions.generated.vardef_client.api.patches_api import (
    PatchesApi,
)
from dapla_metadata.variable_definitions.generated.vardef_client.api.validity_periods_api import (
    ValidityPeriodsApi,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.complete_response import (
    CompleteResponse,
)


class CompletePatchOutput(CompleteResponse):
    """Complete response For internal users who need all details while maintaining variable definitions."""

    @staticmethod
    def from_model(
        model: CompleteResponse,
    ) -> "CompletePatchOutput":
        """Create a CompletePatchOutput instance from a CompleteResponse."""
        return CompletePatchOutput.model_construct(**model.model_dump())

    def __str__(self) -> str:
        """Format as indented JSON."""
        return self.model_dump_json(indent=2)


class VariableDefinition(CompletePatchOutput):
    """A Variable Definition.

    - Provides access to the fields of the specific Variable Definition.
    - Provides methods to access Patches and Validity Periods of this Variable Definition.
    - Provides methods allowing maintenance of this Variable Definition.

    Args:
        CompletePatchOutput: The Pydantic model superclass, representing a Variable Definition.
    """

    @staticmethod
    def from_model(
        model: CompleteResponse,
    ) -> "VariableDefinition":
        """Create a VariableDefinition instance from a CompleteResponse or CompletePatchOutput."""
        return VariableDefinition.model_construct(**model.model_dump())

    def list_validity_periods(self) -> list[CompletePatchOutput]:
        """List all Validity Periods for this Variable Definition."""
        return [
            CompletePatchOutput.from_model(validity_period)
            for validity_period in ValidityPeriodsApi(
                VardefClient.get_client(),
            ).list_validity_periods(
                variable_definition_id=self.id,
            )
        ]

    def list_patches(self) -> list[CompletePatchOutput]:
        """List all Patches for this Variable Definition."""
        return [
            CompletePatchOutput.from_model(patch)
            for patch in PatchesApi(VardefClient.get_client()).list_patches(
                variable_definition_id=self.id,
            )
        ]

    def get_patch(self, patch_id: int) -> CompletePatchOutput:
        """Get a single Patch by ID.

        Args:
            patch_id (int): The ID of the patch.

        Returns:
            CompletePatchOutput: The desired patch.
        """
        return CompletePatchOutput.from_model(
            PatchesApi(VardefClient.get_client()).get_patch(
                variable_definition_id=self.id,
                patch_id=patch_id,
            ),
        )
