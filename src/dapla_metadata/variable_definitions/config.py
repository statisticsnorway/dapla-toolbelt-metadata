from dapla_metadata._shared.config import get_config_item
from dapla_metadata._shared.config import get_dapla_environment
from dapla_metadata._shared.config import get_dapla_group_context
from dapla_metadata._shared.config import get_oidc_token
from dapla_metadata._shared.enums import DaplaEnvironment
from dapla_metadata.variable_definitions.generated.vardef_client.configuration import (
    Configuration,
)

VARDEF_HOST_TEST = "https://metadata.intern.test.ssb.no"


def get_active_group() -> str:
    """Get the group the user currently represents.

    Returns:
        A string with the active group.
    """
    return str(get_dapla_group_context(raising=True))


def get_vardef_host() -> str:
    """Get the host for the server to make requests to.

    Based on standard Dapla platform environment variables, or variables specific
    to Vardef if these are not available.

    Raises:
        NotImplementedError: When Vardef is not available for the current environment.
    """
    match get_dapla_environment():
        case DaplaEnvironment.PROD:
            msg = "Vardef is not available in prod."
            raise NotImplementedError(msg)
        case DaplaEnvironment.TEST:
            return VARDEF_HOST_TEST
        case DaplaEnvironment.DEV:
            msg = "Vardef is not available in dev."
            raise NotImplementedError(msg)
        case _:
            return get_config_item("VARDEF_HOST") or "http://localhost:8080"


def get_vardef_client_configuration() -> Configuration:
    """Build a config to be supplied to the `ApiClient`."""
    return Configuration(
        host=get_vardef_host(),
        access_token=get_oidc_token(raising=True),
    )
