from dapla_metadata.variable_definitions.config import get_vardef_client_configuration
from dapla_metadata.variable_definitions.generated.vardef_client.api.variable_definitions_api import (
    VariableDefinitionsApi,
)
from dapla_metadata.variable_definitions.generated.vardef_client.api_client import (
    ApiClient,
)
from dapla_metadata.variable_definitions.generated.vardef_client.configuration import (
    Configuration,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.complete_response import (
    CompleteResponse,
)


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

    _client: ApiClient | None = None
    _config: Configuration | None = None

    @classmethod
    def get_config(cls) -> Configuration | None:
        """Get the client configuration object."""
        return cls._config

    @classmethod
    def set_config(cls, config: Configuration) -> None:
        """Set the client configuration object."""
        cls._config = config

    @classmethod
    def _get_client(cls) -> ApiClient:
        if not cls._client:
            cls._client = ApiClient(cls._config or get_vardef_client_configuration())
        return cls._client

    @classmethod
    def list_variable_definitions(
        cls,
        date_of_validity: str | None = None,
    ) -> list[CompleteResponse]:
        """List variable definitions.

        ---------
        Filtering
        ---------
        If no filter arguments are provided then all Variable Definitions are returned. See the documentation for the
        individual arguments to understand their effect. Filter arguments are combined with AND logic.

        Args:
            date_of_validity (str | None, optional): List only variable definitions which are valid on this date. Defaults to None.

        Returns:
            list[CompleteResponse]: The list of Variable Definitions.
        """
        return VariableDefinitionsApi(cls._get_client()).list_variable_definitions(
            date_of_validity=date_of_validity,
        )
