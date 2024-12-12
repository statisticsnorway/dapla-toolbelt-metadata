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


class VariableDefinition(CompleteResponse):
    def list_validity_periods(self) -> list[CompleteResponse]:
        return ValidityPeriodsApi(VardefClient.get_client()).list_validity_periods(
            variable_definition_id=self.id,
        )

    def list_patches(self) -> list[CompleteResponse]:
        return PatchesApi(VardefClient.get_client()).list_patches(
            variable_definition_id=self.id,
        )

    def get_patch(self, patch_id: int) -> CompleteResponse:
        return PatchesApi(VardefClient.get_client()).get_patch(
            variable_definition_id=self.id,
            patch_id=patch_id,
        )
