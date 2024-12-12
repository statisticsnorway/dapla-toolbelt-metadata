from dapla_metadata.variable_definitions.config import get_vardef_client_configuration
from dapla_metadata.variable_definitions.generated.vardef_client.api_client import (
    ApiClient,
)
from dapla_metadata.variable_definitions.generated.vardef_client.configuration import (
    Configuration,
)


class VardefClient:
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
    def get_client(cls) -> ApiClient:
        if not cls._client:
            if not cls._config:
                cls._config = get_vardef_client_configuration()
            cls._client = ApiClient(cls._config)
        return cls._client
