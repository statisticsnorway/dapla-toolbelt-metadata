import logging
import os
from datetime import date

from dapla_metadata.variable_definitions.generated import vardef_client
from dapla_metadata.variable_definitions.generated.vardef_client.configuration import (
    Configuration,
)
from dapla_metadata.variable_definitions.generated.vardef_client.exceptions import (
    ApiException,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models import (
    language_string_type,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.complete_response import (
    CompleteResponse,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.draft import (
    Draft,
)
from dapla_metadata.variable_definitions.vardef.errors import VardefClientException

# Configure the logger
logging.basicConfig(
    level=logging.DEBUG,  # Set log level to DEBUG (logs all messages from DEBUG and above)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Define log message format
    handlers=[
        logging.StreamHandler(),  # Output log messages to the console
        logging.FileHandler("app.log", mode="w"),  # Save log messages to a file
    ],
)


class Vardef:
    """Static class."""

    draft = Draft(
        name=language_string_type.LanguageStringType(
            nb=None,
            nn=None,
            en=None,
        ),
        short_name="test908888",
        definition=language_string_type.LanguageStringType(
            nb=None,
            nn=None,
            en=None,
        ),
        classification_reference="91",
        unit_types=["pp"],
        subject_fields=["al"],
        contains_sensitive_personal_information=True,
        measurement_type="01",
        valid_from=date(2024, 11, 1),
        external_reference_uri="http://www.example.com",
        comment=None,
        related_variable_definition_uris=["http://www.example.com"],
        contact=None,
    )

    @staticmethod
    def get_config() -> Configuration | None:
        """Config for connection."""
        host = "http://localhost:8080"
        access_token = os.environ.get("OIDC_TOKEN")
        if access_token is None:
            return None
        return vardef_client.Configuration(
            host=host,
            access_token=access_token,
        )

    @staticmethod
    def create_draft(draft: Draft) -> CompleteResponse | None | dict:
        """Create new variable definition."""
        api_client = vardef_client.ApiClient(configuration=Vardef.get_config())
        api_instance = vardef_client.DraftVariableDefinitionsApi(api_client)
        try:
            return api_instance.create_variable_definition(
                "dapla-felles-developers",
                draft=draft,
            )
        except vardef_client.exceptions.ApiException as e:
            raise VardefClientException(e.body, e.status)

    @staticmethod
    def list_draft() -> list[CompleteResponse] | None:
        """List all variable definitions with status Draft."""
        host = "http://localhost:8080"
        access_token = os.environ.get("OIDC_TOKEN")
        if access_token is None:
            return None
        config = vardef_client.Configuration(
            host=host,
            access_token=access_token,
        )
        api_client = vardef_client.ApiClient(configuration=config)
        api_instance = vardef_client.VariableDefinitionsApi(api_client)
        try:
            return api_instance.list_variable_definitions()
        except vardef_client.exceptions.UnauthorizedException as e:
            logging.info(e.reason)
            return None
        except ApiException as e:
            logging.info(f"API Exception: {e.status} - {e.reason}")  # noqa: G004
            return None
