from datetime import date

from dapla_metadata.variable_definitions.generated.vardef_client.models.person import (
    Person,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.variable_status import (
    VariableStatus,
)
from dapla_metadata.variable_definitions.variable_definition import VariableDefinition
from tests.utils.constants import VARDEF_EXAMPLE_DEFINITION_ID


def test_str(language_string_type, contact, owner):
    variable_definition = VariableDefinition(
        id=VARDEF_EXAMPLE_DEFINITION_ID,
        patch_id=1,
        name=language_string_type,
        short_name="var_test",
        definition=language_string_type,
        classification_reference="91",
        unit_types=["01"],
        subject_fields=["a", "b"],
        contains_special_categories_of_personal_data=True,
        variable_status=VariableStatus.PUBLISHED_EXTERNAL,
        measurement_type="test",
        valid_from=date(2024, 11, 1),
        valid_until=None,
        external_reference_uri="http://www.example.com",
        comment=language_string_type,
        related_variable_definition_uris=["http://www.example.com"],
        contact=contact,
        owner=owner,
        created_at=date(2024, 11, 1),
        created_by=Person(code="724", name="name"),
        last_updated_at=date(2024, 11, 1),
        last_updated_by=Person(code="724", name="name"),
    )
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
  "created_by": {
    "code": "724",
    "name": "name"
  },
  "last_updated_at": "2024-11-01T00:00:00",
  "last_updated_by": {
    "code": "724",
    "name": "name"
  }
}"""
    )
