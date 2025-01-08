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
