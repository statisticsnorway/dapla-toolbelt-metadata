import os
from collections.abc import Generator
from datetime import date
from pathlib import Path

import pytest

from dapla_metadata.variable_definitions._client import VardefClient
from dapla_metadata.variable_definitions.complete_patch_output import DEFAULT_TEMPLATE
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
from dapla_metadata.variable_definitions.generated.vardef_client.models.patch import (
    Patch,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.update_draft import (
    UpdateDraft,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.validity_period import (
    ValidityPeriod,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.variable_status import (
    VariableStatus,
)
from dapla_metadata.variable_definitions.utils.template import create_template_yaml
from dapla_metadata.variable_definitions.variable_definition import CompletePatchOutput
from dapla_metadata.variable_definitions.variable_definition import VariableDefinition
from tests.utils.constants import DAPLA_GROUP_CONTEXT
from tests.utils.constants import VARDEF_EXAMPLE_ACTIVE_GROUP
from tests.utils.constants import VARDEF_EXAMPLE_DEFINITION_ID
from tests.utils.constants import VARDEF_EXAMPLE_INVALID_ID
from tests.utils.microcks_testcontainer import MicrocksContainer


@pytest.fixture(autouse=True)
def _set_dapla_group_context(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv(DAPLA_GROUP_CONTEXT, VARDEF_EXAMPLE_ACTIVE_GROUP)


@pytest.fixture(scope="session")
def client_configuration(vardef_mock_service) -> Configuration:
    return vardef_client.Configuration(
        host=vardef_mock_service.get_mock_url(),
        access_token="test_dummy",  # noqa: S106
    )


@pytest.fixture(autouse=True, scope="session")
def _configure_vardef_client(client_configuration):
    VardefClient.set_config(client_configuration)


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
        unit_types=["01"],
        subject_fields=["a", "b"],
        contains_special_categories_of_personal_data=True,
        measurement_type="test",
        valid_from=date(2024, 11, 1),
        external_reference_uri="http://www.example.com",
        comment=language_string_type,
        related_variable_definition_uris=["http://www.example.com"],
        contact=contact,
    )


def sample_variable_definition() -> VariableDefinition:
    return VariableDefinition(
        id=VARDEF_EXAMPLE_DEFINITION_ID,
        patch_id=1,
        name=LanguageStringType(nb="test", nn="test", en="test"),
        short_name="var_test",
        definition=LanguageStringType(nb="test", nn="test", en="test"),
        classification_reference="91",
        unit_types=["01"],
        subject_fields=["a", "b"],
        contains_special_categories_of_personal_data=True,
        variable_status=VariableStatus.PUBLISHED_EXTERNAL,
        measurement_type="test",
        valid_from=date(2024, 11, 1),
        valid_until=None,
        external_reference_uri="http://www.example.com",
        comment=LanguageStringType(nb="test", nn="test", en="test"),
        related_variable_definition_uris=["http://www.example.com"],
        contact=Contact(
            title=LanguageStringType(nb="test", nn="test", en="test"),
            email="me@example.com",
        ),
        owner=Owner(team="my_team", groups=["my_team_developers"]),
        created_at=date(2024, 11, 1),
        created_by="ano@ssb.no",
        last_updated_at=date(2024, 11, 1),
        last_updated_by="ano@ssb.no",
    )


def unknown_variable_definition() -> VariableDefinition:
    unknown = sample_variable_definition()
    unknown.id = VARDEF_EXAMPLE_INVALID_ID
    return unknown


@pytest.fixture
def variable_definition() -> VariableDefinition:
    return sample_variable_definition()


@pytest.fixture
def update_draft(language_string_type, contact, owner) -> UpdateDraft:
    return UpdateDraft(
        name=language_string_type,
        short_name="test",
        definition=language_string_type,
        classification_reference="91",
        unit_types=["a", "b"],
        subject_fields=["a", "b"],
        contains_special_categories_of_personal_data=True,
        variable_status=VariableStatus.PUBLISHED_EXTERNAL,
        measurement_type="test",
        valid_from=date(2024, 11, 1),
        external_reference_uri="http://www.example.com",
        comment=language_string_type,
        related_variable_definition_uris=["http://www.example.com"],
        contact=contact,
        owner=owner,
    )


@pytest.fixture
def validity_period(language_string_type, contact) -> ValidityPeriod:
    return ValidityPeriod(
        name=language_string_type,
        definition=language_string_type,
        classification_reference="91",
        unit_types=["a", "b"],
        subject_fields=["a", "b"],
        contains_special_categories_of_personal_data=True,
        variable_status=VariableStatus.PUBLISHED_EXTERNAL,
        measurement_type="test",
        valid_from=date(2024, 11, 1),
        external_reference_uri="http://www.example.com",
        comment=language_string_type,
        related_variable_definition_uris=["http://www.example.com"],
        contact=contact,
    )


@pytest.fixture
def patch(language_string_type, contact, owner) -> Patch:
    return Patch(
        name=language_string_type,
        definition=language_string_type,
        classification_reference="91",
        unit_types=["a", "b"],
        subject_fields=["a", "b"],
        contains_special_categories_of_personal_data=True,
        variable_status=VariableStatus.PUBLISHED_EXTERNAL,
        measurement_type="test",
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


def sample_complete_patch_output() -> CompletePatchOutput:
    return CompletePatchOutput(
        id=VARDEF_EXAMPLE_DEFINITION_ID,
        patch_id=1,
        name=LanguageStringType(nb="test", nn="test", en="test"),
        short_name="var_test",
        definition=LanguageStringType(nb="test", nn="test", en="test"),
        classification_reference="91",
        unit_types=["01"],
        subject_fields=["a", "b"],
        contains_special_categories_of_personal_data=True,
        variable_status=VariableStatus.PUBLISHED_INTERNAL,
        measurement_type="test",
        valid_from=date(2024, 11, 1),
        valid_until=None,
        external_reference_uri="http://www.example.com",
        comment=LanguageStringType(nb="test", nn="test", en="test"),
        related_variable_definition_uris=["http://www.example.com"],
        contact=Contact(
            title=LanguageStringType(nb="test", nn="test", en="test"),
            email="me@example.com",
        ),
        owner=Owner(team="my_team", groups=["my_team_developers"]),
        created_at=date(2024, 11, 1),
        created_by="ano@ssb.no",
        last_updated_at=date(2024, 11, 1),
        last_updated_by="ano@ssb.no",
    )


@pytest.fixture
def complete_patch_output() -> CompletePatchOutput:
    return sample_complete_patch_output()


def _clean_up_after_test(target_path: Path, base_path: Path):
    if target_path.exists():
        target_path.unlink()
    if base_path.exists():
        base_path.rmdir()


@pytest.fixture
def set_temp_workspace(tmp_path: Path):
    """Fixture which set env WORKSPACE_DIR to tmp path/work."""
    workspace_dir = tmp_path / "work"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    os.environ["WORKSPACE_DIR"] = str(workspace_dir)
    return workspace_dir


@pytest.fixture
def work_folder_defaults(set_temp_workspace: Path):
    """Fixture that ensures a work folder exists for template with default values."""
    base_path = set_temp_workspace
    file_name = create_template_yaml(
        DEFAULT_TEMPLATE,
        custom_directory=base_path,
    )

    target_path = base_path / file_name

    yield target_path

    _clean_up_after_test(target_path, base_path)


@pytest.fixture
def work_folder_saved_variable(set_temp_workspace: Path):
    """Fixture that ensures a work folder exists for template with saved variable definition values."""
    base_path = set_temp_workspace
    file_name = create_template_yaml(
        sample_complete_patch_output(),
        custom_directory=base_path,
    )
    target_path = base_path / file_name
    yield target_path

    _clean_up_after_test(target_path, base_path)


@pytest.fixture
def _delete_workspace_dir_env_var():
    original_workspace_dir = os.environ.get("WORKSPACE_DIR")

    if "WORKSPACE_DIR" in os.environ:
        del os.environ["WORKSPACE_DIR"]

    yield

    if original_workspace_dir is not None:
        os.environ["WORKSPACE_DIR"] = original_workspace_dir
    else:
        pass
