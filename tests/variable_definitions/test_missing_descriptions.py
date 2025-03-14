from unittest.mock import MagicMock
from unittest.mock import patch

from dapla_metadata.variable_definitions._utils.descriptions import (
    apply_norwegian_descriptions_to_model,
)


@patch("dapla_metadata.variable_definitions._utils.descriptions.logger")
@patch(
    "dapla_metadata.variable_definitions._utils.descriptions.load_descriptions",
    lambda _: {},
)
def test_apply_descriptions_logs_missing_description(
    mock_logger: MagicMock,
):
    mock_field_info = MagicMock()
    mock_class = MagicMock()
    mock_class.model_fields = {"name": mock_field_info}
    mock_class = MagicMock()
    mock_class.model_fields = {"name": mock_field_info}

    apply_norwegian_descriptions_to_model(mock_class)

    # Assert that the json_schema_extra is correctly updated
    assert (
        mock_class.model_fields["name"].json_schema_extra["norwegian_description"]
        == "No description in norwegian found for name"
    )

    mock_logger.warning.assert_called_once_with(
        "Missing description for %s",
        "name",
    )
