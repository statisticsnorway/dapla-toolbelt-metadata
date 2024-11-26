from collections.abc import Generator
from datetime import date

import pytest
from tests.utils.microcks_testcontainer import MicrocksContainer

from dapla_metadata.variable_definitions.generated import vardef_client
from dapla_metadata.variable_definitions.generated.vardef_client.api_client import (
    ApiClient,
)
from dapla_metadata.variable_definitions.generated.vardef_client.configuration import (
    Configuration,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.contact import (
    Contact,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.draft import (
    Draft,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.language_string_type import (
    LanguageStringType,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.owner import (
    Owner,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.update_draft import (
    UpdateDraft,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.variable_status import (
    VariableStatus,
)


@pytest.fixture
def client_configuration() -> Configuration:
    return vardef_client.Configuration(
        host="http://localhost",
        access_token="test_dummy",  # noqa: S106
    )


@pytest.fixture
def api_client(client_configuration) -> Generator[ApiClient]:
    with vardef_client.ApiClient(client_configuration) as api_client:
        yield api_client


@pytest.fixture
def language_string_type() -> LanguageStringType:
    return LanguageStringType(nb="test", nn="test", en="test")


@pytest.fixture
def contact(language_string_type) -> Contact:
    return Contact(title=language_string_type, email="me@example.com")


@pytest.fixture
def owner() -> Owner:
    return Owner(team="my_team", groups=["my_team_developers"])


@pytest.fixture
def draft(language_string_type, contact) -> Draft:
    return Draft(
        name=language_string_type,
        short_name="test",
        definition=language_string_type,
        classification_reference="91",
        unit_types=["a", "b"],
        subject_fields=["a", "b"],
        contains_sensitive_personal_information=True,
        measurement_type="test",
        valid_from=date(2024, 11, 1),
        external_reference_uri="http://www.example.com",
        comment=language_string_type,
        related_variable_definition_uris=["http://www.example.com"],
        contact=contact,
    )


@pytest.fixture
def update_draft(language_string_type, contact, owner) -> UpdateDraft:
    return UpdateDraft(
        name=language_string_type,
        short_name="test",
        definition=language_string_type,
        classification_reference="91",
        unit_types=["a", "b"],
        subject_fields=["a", "b"],
        contains_sensitive_personal_information=True,
        variable_status=VariableStatus.PUBLISHED_EXTERNAL,
        measurement_type="test",
        valid_from=date(2024, 11, 1),
        external_reference_uri="http://www.example.com",
        comment=language_string_type,
        related_variable_definition_uris=["http://www.example.com"],
        contact=contact,
        owner=owner,
    )


@pytest.fixture(scope="session")
def vardef_mock_service(
    openapi_definition: str = "tests/variable_definitions/resources/variable-definitions-0.1.yml",
):
    with MicrocksContainer() as container:
        container.upload_primary_artifact(openapi_definition)
        yield container
