import ruamel.yaml

from dapla_metadata.variable_definitions._generated.vardef_client.models.variable_status import (
    VariableStatus,
)

yaml = ruamel.yaml.YAML()

from dapla_metadata.variable_definitions.vardef import Vardef
from tests.utils.constants import VARDEF_EXAMPLE_DEFINITION_ID
from tests.utils.constants import VARDEF_EXAMPLE_SHORT_NAME


def test_write_existing_variable_to_file():
    file_name = (
        Vardef.get_variable_definition_by_id(
            variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
        )
        .to_file()
        .get_file_path()
    )
    with file_name.open(encoding="utf-8") as f:
        parsed_yaml = yaml.load(f)

    assert parsed_yaml["variable_status"] == VariableStatus.DRAFT
    assert parsed_yaml["short_name"] == VARDEF_EXAMPLE_SHORT_NAME


def test_write_existing_variable_to_file_by_short_name():
    file_name = (
        Vardef.get_variable_definition_by_shortname(
            short_name=VARDEF_EXAMPLE_SHORT_NAME,
        )
        .to_file()
        .get_file_path()
    )
    with file_name.open(encoding="utf-8") as f:
        parsed_yaml = yaml.load(f)

    assert parsed_yaml["variable_status"] == VariableStatus.DRAFT
    assert parsed_yaml["short_name"] == VARDEF_EXAMPLE_SHORT_NAME


def test_shortname_and_id_in_filename():
    file_name = (
        Vardef.get_variable_definition_by_id(
            variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
        )
        .to_file()
        .get_file_path()
    )

    assert (
        f"variable_definition_{VARDEF_EXAMPLE_SHORT_NAME}_{VARDEF_EXAMPLE_DEFINITION_ID}_"
        in str(file_name)
    )
