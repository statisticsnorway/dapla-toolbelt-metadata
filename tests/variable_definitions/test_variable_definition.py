from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from dapla_metadata.variable_definitions.exceptions import VardefFileError
from dapla_metadata.variable_definitions.generated.vardef_client.models.patch import (
    Patch,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.update_draft import (
    UpdateDraft,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.validity_period import (
    ValidityPeriod,
)
from dapla_metadata.variable_definitions.vardef import Vardef
from dapla_metadata.variable_definitions.variable_definition import CompletePatchOutput
from dapla_metadata.variable_definitions.variable_definition import VariableDefinition
from tests.utils.constants import VARDEF_EXAMPLE_DATE
from tests.utils.constants import VARDEF_EXAMPLE_DEFINITION_ID
from tests.variable_definitions.constants import VARIABLE_DEFINITION_EDITING_FILES_DIR
from tests.variable_definitions.test_vardef import PATCH_ID


def test_list_patches():
    landbak = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert isinstance(landbak.list_patches()[0], CompletePatchOutput)


def test_get_patch():
    landbak = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert isinstance(landbak.get_patch(1), CompletePatchOutput)


def test_list_validity_periods():
    landbak = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert isinstance(landbak.list_validity_periods()[0], CompletePatchOutput)


def test_update_draft(
    update_draft: UpdateDraft,
):
    my_draft = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert isinstance(my_draft.update_draft(update_draft), CompletePatchOutput)


def test_delete_draft():
    my_draft = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert my_draft.id is not None
    result = my_draft.delete_draft()
    assert result == f"Variable {VARDEF_EXAMPLE_DEFINITION_ID} safely deleted"


def test_create_patch(
    patch: Patch,
    variable_definition: VariableDefinition,
):
    my_variable = variable_definition
    assert my_variable.patch_id == 1
    created_patch = my_variable.create_patch(
        patch=patch,
        valid_from=VARDEF_EXAMPLE_DATE,
    )
    assert isinstance(
        created_patch,
        CompletePatchOutput,
    )
    assert created_patch.patch_id == PATCH_ID


def test_create_validity_period(
    validity_period: ValidityPeriod,
    variable_definition: VariableDefinition,
):
    my_variable = variable_definition
    assert isinstance(
        my_variable.create_validity_period(validity_period),
        CompletePatchOutput,
    )


def test_update_draft_from_file():
    my_draft = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    ).to_file()
    assert isinstance(my_draft.update_draft_from_file(), CompletePatchOutput)


def test_update_draft_from_file_no_known_file():
    with pytest.raises(ValueError, match="Could not deduce a path to the file"):
        Vardef.get_variable_definition_by_id(
            VARDEF_EXAMPLE_DEFINITION_ID,
        ).update_draft_from_file()


def test_update_draft_from_file_file_non_existent():
    with pytest.raises(FileNotFoundError):
        Vardef.get_variable_definition_by_id(
            VARDEF_EXAMPLE_DEFINITION_ID,
        ).update_draft_from_file("my_cool_file.yaml")


def test_update_draft_from_file_invalid_yaml(tmp_path: Path):
    invalid = tmp_path / "invalid_yaml.yaml"
    invalid.write_text(
        """--- invalid yaml ---
not allowed:
:why
""",
    )
    with pytest.raises(VardefFileError):
        Vardef.get_variable_definition_by_id(
            VARDEF_EXAMPLE_DEFINITION_ID,
        ).update_draft_from_file(
            invalid,
        )


def test_update_draft_from_file_validation_fails(tmp_path: Path):
    invalid = tmp_path / "fails_validation.yaml"
    invalid.write_text(
        """fails validation""",
    )
    with pytest.raises(ValidationError):
        Vardef.get_variable_definition_by_id(
            VARDEF_EXAMPLE_DEFINITION_ID,
        ).update_draft_from_file(
            invalid,
        )


def test_update_draft_from_file_specify_file():
    assert (
        Vardef.get_variable_definition_by_id(
            VARDEF_EXAMPLE_DEFINITION_ID,
        )
        .update_draft_from_file(
            VARIABLE_DEFINITION_EDITING_FILES_DIR / "classification_reference.yaml",
        )
        .short_name
        == "landbak"
    )


def test_create_patch_from_file(variable_definition: VariableDefinition):
    mock_api_response = MagicMock(name="VariableDefinition")
    mock_api_response.classification_reference = "702"
    with patch.object(
        VariableDefinition,
        "create_patch",
        return_value=mock_api_response,
    ) as mock_create_patch:
        my_patch = variable_definition
        result = my_patch.create_patch_from_file(
            file_path=VARIABLE_DEFINITION_EDITING_FILES_DIR
            / "classification_reference.yaml",
        )

    assert my_patch.classification_reference != result.classification_reference
    mock_create_patch.assert_called_once()


def test_create_patch_from_file_path_not_set(variable_definition: VariableDefinition):
    my_patch = variable_definition
    my_patch.set_file_path(file_path=None)
    with pytest.raises(ValueError, match="Could not deduce a path to the file"):
        my_patch.create_patch_from_file()


def test_create_patch_from_file_path_non_existing(
    variable_definition: VariableDefinition,
):
    my_patch = variable_definition
    with pytest.raises(FileNotFoundError):
        my_patch.create_patch_from_file("some_file.yaml")


def test_str(variable_definition):
    assert (
        str(variable_definition)
        == """{
  "id": "wypvb3wd",
  "patch_id": 1,
  "name": {
    "nb": "test",
    "nn": "test",
    "en": "test"
  },
  "short_name": "var_test",
  "definition": {
    "nb": "test",
    "nn": "test",
    "en": "test"
  },
  "classification_reference": "91",
  "unit_types": [
    "01"
  ],
  "subject_fields": [
    "a",
    "b"
  ],
  "contains_special_categories_of_personal_data": true,
  "variable_status": "PUBLISHED_EXTERNAL",
  "measurement_type": "test",
  "valid_from": "2024-11-01",
  "valid_until": null,
  "external_reference_uri": "http://www.example.com",
  "comment": {
    "nb": "test",
    "nn": "test",
    "en": "test"
  },
  "related_variable_definition_uris": [
    "http://www.example.com"
  ],
  "owner": {
    "team": "my_team",
    "groups": [
      "my_team_developers"
    ]
  },
  "contact": {
    "title": {
      "nb": "test",
      "nn": "test",
      "en": "test"
    },
    "email": "me@example.com"
  },
  "created_at": "2024-11-01T00:00:00",
  "created_by": "ano@ssb.no",
  "last_updated_at": "2024-11-01T00:00:00",
  "last_updated_by": "ano@ssb.no"
}"""
    )
