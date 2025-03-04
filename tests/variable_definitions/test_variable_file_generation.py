import pytest
import ruamel.yaml

from dapla_metadata.variable_definitions.utils.variable_definition_files import (
    _get_workspace_dir,
)

yaml = ruamel.yaml.YAML()

from dapla_metadata.variable_definitions.vardef import Vardef
from tests.utils.constants import VARDEF_EXAMPLE_DEFINITION_ID
from tests.utils.constants import VARDEF_EXAMPLE_SHORT_NAME

PATCH_ID = 2


@pytest.mark.usefixtures("set_temp_workspace")
def test_write_existing_variable_to_file():
    file_name = Vardef.write_variable_to_file(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    ).get_file_path()

    target_path = _get_workspace_dir() / file_name

    with target_path.open(encoding="utf-8") as f:
        parsed_yaml = yaml.load(f)

    assert parsed_yaml["variable_status"] == "DRAFT"
    assert parsed_yaml["short_name"] == "landbak"


@pytest.mark.usefixtures("set_temp_workspace")
def test_write_existing_variable_to_file_by_short_name():
    file_name = Vardef.write_variable_to_file(
        short_name=VARDEF_EXAMPLE_SHORT_NAME,
    ).get_file_path()

    target_path = _get_workspace_dir() / file_name

    with target_path.open(encoding="utf-8") as f:
        parsed_yaml = yaml.load(f)

    assert parsed_yaml["variable_status"] == "DRAFT"
    assert parsed_yaml["short_name"] == "landbak"


@pytest.mark.usefixtures("set_temp_workspace")
def test_write_variable_to_file_no_parameters():
    with pytest.raises(ValueError, match="One of"):
        Vardef.write_variable_to_file()


@pytest.mark.usefixtures("set_temp_workspace")
def test_write_variable_to_file_two_parameters():
    with pytest.raises(ValueError, match="Only one of"):
        Vardef.write_variable_to_file(
            variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
            short_name=VARDEF_EXAMPLE_SHORT_NAME,
        )


@pytest.mark.usefixtures("set_temp_workspace")
def test_shortname_and_id_in_filename():
    file_name = Vardef.write_variable_to_file(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    ).get_file_path()

    assert "variable_definition_landbak_wypvb3wd_" in str(file_name)


@pytest.mark.usefixtures("set_temp_workspace")
def test_shortname_and_id_not_in_filename():
    file_name = Vardef.write_variable_to_file(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    ).get_file_path()

    assert "variable_definition_" in str(file_name)
