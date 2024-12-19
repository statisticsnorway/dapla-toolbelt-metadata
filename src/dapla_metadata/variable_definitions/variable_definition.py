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


class CompletePatchOutput(CompleteResponse):
    """Complete response For internal users who need all details while maintaining variable definitions."""

    @staticmethod
    def from_model(
        model: CompleteResponse,
    ) -> "CompletePatchOutput":
        """Create a CompletePatchOutput instance from a CompletePatchOutput."""
        return CompletePatchOutput.model_construct(**model.model_dump())

    def __str__(self) -> str:
        """Format as indented JSON."""
        return self.model_dump_json(indent=2, warnings=False)


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
        """Create a VariableDefinition instance from a CompletePatchOutput or CompletePatchOutput."""
        return VariableDefinition.model_construct(**model.model_dump())

    @vardef_exception_handler
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

    @vardef_exception_handler
    def list_patches(self) -> list[CompletePatchOutput]:
        """List all Patches for this Variable Definition."""
        return [
            CompletePatchOutput.from_model(patch)
            for patch in PatchesApi(VardefClient.get_client()).list_patches(
                variable_definition_id=self.id,
            )
        ]

    @vardef_exception_handler
    def update_draft(
        self,
        update_draft: UpdateDraft,
    ) -> CompletePatchOutput:
        """Update this Variable Definition.

        - Variable definition must have status 'DRAFT'.
        - Supply only the fields to be changed. Other fields will retain their current values.

        Args:
            update_draft: The input with updated values.

        Returns:
            CompletePatchOutput: Updated Variable definition with all details.
        """
        return CompletePatchOutput.from_model(
            DraftVariableDefinitionsApi(
                VardefClient.get_client(),
            ).update_variable_definition_by_id(
                variable_definition_id=self.id,
                active_group=config.get_active_group(),
                update_draft=update_draft,
            ),
        )

    @vardef_exception_handler
    def delete_draft(
        self,
    ) -> str:
        """Delete this Variable definition.

        Variable definition must have status 'DRAFT'.

        Returns:
            str: A message if the operation was succsessful.

        """
        DraftVariableDefinitionsApi(
            VardefClient.get_client(),
        ).delete_variable_definition_by_id(
            variable_definition_id=self.id,
            active_group=config.get_active_group(),
        )
        return f"Variable {self.id} safely deleted"

    @vardef_exception_handler
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

    @vardef_exception_handler
    def create_patch(
        self,
        patch: Patch,
        valid_from: date | None = None,
    ) -> CompletePatchOutput:
        """Create a new Patch for this Variable Definition.

        Patches are to be used for minor changes which don't require a new Validity Period.
        Examples of reasons for creating a new Patch:
          - Correcting a typo
          - Adding a translation
          - Adding a subject field

        Supply only the fields to be changed. Other fields will retain their current values.

        Args:
            patch: The input for a new patch.
            valid_from: Optional date for selecting a Validity Period to create patch in. The date must
                        exactly match the Validity Period `valid_from`. If value is None the patch is
                        created in the last validity period.

        Returns:
            CompletePatchOutput: Variable Definition with all details.

        """
        return CompletePatchOutput.from_model(
            PatchesApi(
                VardefClient.get_client(),
            ).create_patch(
                variable_definition_id=self.id,
                active_group=config.get_active_group(),
                patch=patch,
                valid_from=valid_from,
            ),
        )

    @vardef_exception_handler
    def create_validity_period(
        self,
        validity_period: ValidityPeriod,
    ) -> CompletePatchOutput:
        """Create a new Validity Period for this Variable Definition.

        In order to create a new Validity Period input must contain updated
        'definition' text for all present languages and a new valid from.

        A new Validity Period should be created only when the fundamental definition
        of the variable has changed. This way the previous definition can be preserved
        for use in historical data.

        Args:
            validity_period: The input for new Validity Period

        Returns:
            CompletePatchOutput: Variable Definition with all details.
        """
        return CompletePatchOutput.from_model(
            ValidityPeriodsApi(
                VardefClient.get_client(),
            ).create_validity_period(
                variable_definition_id=self.id,
                active_group=config.get_active_group(),
                validity_period=validity_period,
            ),
        )
