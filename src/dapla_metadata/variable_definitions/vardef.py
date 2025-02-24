from datetime import date

from dapla_metadata.variable_definitions import config
from dapla_metadata.variable_definitions._client import VardefClient
from dapla_metadata.variable_definitions.exceptions import VariableNotFoundError
from dapla_metadata.variable_definitions.exceptions import vardef_exception_handler
from dapla_metadata.variable_definitions.generated.vardef_client.api.data_migration_api import (
    DataMigrationApi,
)
from dapla_metadata.variable_definitions.generated.vardef_client.api.draft_variable_definitions_api import (
    DraftVariableDefinitionsApi,
)
from dapla_metadata.variable_definitions.generated.vardef_client.api.variable_definitions_api import (
    VariableDefinitionsApi,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.draft import (
    Draft,
)
from dapla_metadata.variable_definitions.utils.template import (
    model_to_yaml_with_comments,
)
from dapla_metadata.variable_definitions.variable_definition import VariableDefinition


class Vardef:
    """Create, maintain and read Variable Definitions.

    ====================
    Variable Definitions
    ====================

    Variable Definitions are centralized definitions of concrete variables which are typically present in multiple datasets. Variable Definitions
    support standardization of data and metadata and facilitate sharing and joining of data by clarifying when variables have an identical
    definition.

    The methods in this class allow for creation, maintenance and access of Variable Definitions.

    Creation and maintenance of variables may only be performed by Statistics Norway employees representing a specific Dapla team, who are defined
    as the owners of a given Variable Definition. The group a user represents is chosen when starting a service in Dapla Lab. This class will
    seamlessly detect this and send it to the API. All maintenance is to be performed by the owners, with no intervention from administrators.

    ======
    Status
    ======
    All Variable Definitions have an associated status. The possible values for status are `DRAFT`, `PUBLISHED_INTERNAL` and `PUBLISHED_EXTERNAL`.

    -----
    Draft
    -----
    When a Variable Definition is created it is assigned the status `DRAFT`. Under this status the Variable Definition is:
    * Only visible to Statistics Norway employees.
    * Mutable (it may be changed directly without need for versioning).
    * Not suitable to refer to from other systems.
    This status may be changed to `PUBLISHED_INTERNAL` or `PUBLISHED_EXTERNAL` with a direct update.

    ------------------
    Published Internal
    ------------------
    Under this status the Variable Definition is:
    * Only visible to Statistics Norway employees.
    * Immutable (all changes are versioned).
    * Suitable to refer to in internal systems for statistics production.
    * Not suitable to refer to for external use (for example in Statistikkbanken).

    This status may be changed to `PUBLISHED_EXTERNAL` by creating a Patch version.

    ------------------
    Published External
    ------------------
    Under this status the Variable Definition is:
    * Visible to the general public.
    * Immutable (all changes are versioned).
    * Suitable to refer to from any system.

    This status may not be changed as it would break immutability. If a Variable Definition is no longer relevant then its period of validity
    should be ended by specifying a `valid_until` date in a Patch version.

    ============
    Immutability
    ============
    Variable Definitions are immutable. This means that any changes must be performed in a strict versioning system. Consumers can avoid
    being exposed to breaking changes by specifying a `date_of_validity` when they request a Variable Definition.
    """

    @classmethod
    @vardef_exception_handler
    def create_draft(cls, draft: Draft) -> VariableDefinition:
        """Create a Draft Variable Definition."""
        return VariableDefinition.from_model(
            DraftVariableDefinitionsApi(
                VardefClient.get_client(),
            ).create_variable_definition(
                active_group=config.get_active_group(),
                draft=draft,
            ),
        )

    @classmethod
    @vardef_exception_handler
    def migrate_from_vardok(cls, vardok_id: str) -> VariableDefinition:
        """Migrate a Variable Definition from Vardok to Vardef.

        - Each Vardok Variable Definition may only be migrated once.
        - The Dapla team of the person who performs the migration will be set as the owner.
        - All metadata should be checked for correctness before publication.

        Args:
            vardok_id (str): The ID of a Variable Definition in Vardok.

        Returns:
            VariableDefinition: The migrated Variable Definition in Vardef.
        """
        return VariableDefinition.from_model(
            DataMigrationApi(
                VardefClient.get_client(),
            ).create_variable_definition_from_var_dok(
                active_group=config.get_active_group(),
                vardok_id=vardok_id,
            ),
        )

    @classmethod
    @vardef_exception_handler
    def list_variable_definitions(
        cls,
        date_of_validity: date | None = None,
    ) -> list[VariableDefinition]:
        """List variable definitions.

        ---------
        Filtering
        ---------
        If no filter arguments are provided then all Variable Definitions are returned. See the documentation for the
        individual arguments to understand their effect. Filter arguments are combined with AND logic.

        Args:
            date_of_validity (date | None, optional): List only variable definitions which are valid on this date. Defaults to None.

        Returns:
            list[VariableDefinition]: The list of Variable Definitions.
        """
        return [
            VariableDefinition.from_model(definition)
            for definition in VariableDefinitionsApi(
                VardefClient.get_client(),
            ).list_variable_definitions(
                date_of_validity=date_of_validity,
            )
        ]

    @classmethod
    @vardef_exception_handler
    def get_variable_definition(
        cls,
        variable_definition_id: str | None = None,
        short_name: str | None = None,
        date_of_validity: date | None = None,
    ) -> VariableDefinition:
        """Retrieve a Variable Definition by ID or short name.

        Args:
            variable_definition_id (str | None): The ID of the Variable Definition.
            short_name (str | None): The short name of the Variable Definition.
            date_of_validity (date | None, optional): Filter by validity date. Defaults to None.

        Returns:
            VariableDefinition: The retrieved Variable Definition.

        Raises:
            ValueError: If both `variable_definition_id` and `short_name` are provided.
            NotFoundException: If no matching Variable Definition is found.
        """
        if variable_definition_id and short_name:
            msg = "Specify either 'variable_definition_id' or 'short_name', not both."
            raise ValueError(
                msg,
            )

        if variable_definition_id is None and short_name is None:
            msg = "Must specify either 'variable_definition_id' or 'short_name'."
            raise ValueError(
                msg,
            )

        client = VardefClient.get_client()
        api = VariableDefinitionsApi(client)

        if short_name:
            v = api.list_variable_definitions(
                short_name=short_name,
                date_of_validity=date_of_validity,
            )
            if len(v) == 0:
                msg = f"Variable with short name %s{short_name} not found"
                raise VariableNotFoundError(msg)

            return VariableDefinition.from_model(
                api.list_variable_definitions(
                    short_name=short_name,
                    date_of_validity=date_of_validity,
                )[0],
            )

        return VariableDefinition.from_model(
            api.get_variable_definition_by_id(
                variable_definition_id=variable_definition_id,
                date_of_validity=date_of_validity,
            ),
        )

    @classmethod
    def write_template_to_file(cls) -> str:
        """Write template with default values to a yaml file."""
        file_path = model_to_yaml_with_comments()
        # Check if the file was created
        if not file_path.exists():
            return "Error: File was not created"
        return "Successfully written to file"
