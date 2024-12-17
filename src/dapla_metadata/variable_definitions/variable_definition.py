from datetime import date

from dapla_metadata.variable_definitions import config
from dapla_metadata.variable_definitions._client import VardefClient
from dapla_metadata.variable_definitions.exceptions import vardef_exception_handler
from dapla_metadata.variable_definitions.generated.vardef_client.api.draft_variable_definitions_api import (
    DraftVariableDefinitionsApi,
)
from dapla_metadata.variable_definitions.generated.vardef_client.api.patches_api import (
    PatchesApi,
)
from dapla_metadata.variable_definitions.generated.vardef_client.api.validity_periods_api import (
    ValidityPeriodsApi,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.complete_response import (
    CompleteResponse,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.patch import (
    Patch,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.update_draft import (
    UpdateDraft,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.validity_period import (
    ValidityPeriod,
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

    @vardef_exception_handler
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

    @vardef_exception_handler
    def update_draft(
        self,
        update_draft: UpdateDraft,
    ) -> CompleteResponse:
        """Update a Draft variable definition."""
        return DraftVariableDefinitionsApi(
            VardefClient.get_client(),
        ).update_variable_definition_by_id(
            variable_definition_id=self.id,
            active_group=config.get_active_group(),
            update_draft=update_draft,
        )

    @vardef_exception_handler
    def delete_draft(
        self,
    ) -> str:
        """Update a Draft variable definition."""
        DraftVariableDefinitionsApi(
            VardefClient.get_client(),
        ).delete_variable_definition_by_id(
            variable_definition_id=self.id,
            active_group=config.get_active_group(),
        )
        return f"Variable {self.id} safely deleted"

    @vardef_exception_handler
    def create_patch(
        self,
        patch: Patch,
        valid_from: date | None = None,
    ) -> CompleteResponse:
        """Create new patch for variable definition."""
        return PatchesApi(
            VardefClient.get_client(),
        ).create_patch(
            variable_definition_id=self.id,
            active_group=config.get_active_group(),
            patch=patch,
            valid_from=valid_from,
        )

    @vardef_exception_handler
    def create_validity_period(
        self,
        validity_period: ValidityPeriod,
    ) -> CompleteResponse:
        """Create new validity period for variable definition.

        New period must have new defintion text for all languages present and new valid from.
        """
        return ValidityPeriodsApi(
            VardefClient.get_client(),
        ).create_validity_period(
            variable_definition_id=self.id,
            active_group=config.get_active_group(),
            validity_period=validity_period,
        )
