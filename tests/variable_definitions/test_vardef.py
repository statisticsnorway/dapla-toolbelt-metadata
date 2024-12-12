from dapla_metadata.variable_definitions._client import VardefClient
from dapla_metadata.variable_definitions.generated.vardef_client.configuration import (
    Configuration,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.complete_response import (
    CompleteResponse,
)
from dapla_metadata.variable_definitions.vardef import Vardef
from dapla_metadata.variable_definitions.variable_definition import VariableDefinition
from tests.utils.constants import VARDEF_EXAMPLE_DATE
from tests.utils.constants import VARDEF_EXAMPLE_DEFINITION_ID


def test_list_variable_definitions(client_configuration: Configuration):
    VardefClient.set_config(client_configuration)
    assert Vardef.list_variable_definitions() == []


def test_list_variable_definitions_with_date_of_validity(
    client_configuration: Configuration,
):
    VardefClient.set_config(client_configuration)
    assert isinstance(
        Vardef.list_variable_definitions(date_of_validity=VARDEF_EXAMPLE_DATE)[0],
        CompleteResponse,
    )


def test_get_variable_definition(client_configuration: Configuration):
    VardefClient.set_config(client_configuration)
    landbak = Vardef.get_variable_definition(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert isinstance(landbak, VariableDefinition)
    assert landbak.classification_reference == "91"


def test_list_patches(client_configuration: Configuration):
    VardefClient.set_config(client_configuration)
    landbak = Vardef.get_variable_definition(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert isinstance(landbak.list_patches()[0], CompleteResponse)


def test_get_patch(client_configuration: Configuration):
    VardefClient.set_config(client_configuration)
    landbak = Vardef.get_variable_definition(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert isinstance(landbak.get_patch(1), CompleteResponse)


def test_list_validity_periods(client_configuration: Configuration):
    VardefClient.set_config(client_configuration)
    landbak = Vardef.get_variable_definition(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert isinstance(landbak.list_validity_periods()[0], CompleteResponse)
