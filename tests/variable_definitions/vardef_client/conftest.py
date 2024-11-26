from collections.abc import Generator
from datetime import date

import pytest
import requests
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.generic import ServerContainer

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


@pytest.fixture(scope="session")
def vardef_mock_service(
    image_name: str = "quay.io/microcks/microcks-uber:1.10.1-native",
):
    print(f"Starting container with image: {image_name}")
    with ServerContainer(
        image=image_name,
        port=9000,
    ) as container:
        print(f"Started container: {image_name}\n{container}")
        url = container._create_connection_url()  # noqa: SLF001
        print("Waiting for liveness")
        response = requests.get(f"{url}", timeout=5)
        assert response.status_code == 200, "Response status code is not 200"
        print("Waiting for logs")
        wait_for_logs(
            container=container,
            predicate=".*Started MicrocksApplication.*",
            timeout=1,
        )
        yield url
