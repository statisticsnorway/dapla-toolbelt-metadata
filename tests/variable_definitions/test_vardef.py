from dapla_metadata.variable_definitions.generated.vardef_client.configuration import (
    Configuration,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.complete_response import (
    CompleteResponse,
)
from dapla_metadata.variable_definitions.vardef import Vardef
from tests.utils.constants import VARDEF_EXAMPLE_DATE
from tests.utils.constants import VARDEF_EXAMPLE_DEFINITION_ID


def test_list_variable_definitions(client_configuration: Configuration):
    Vardef.set_config(client_configuration)
    assert Vardef.list_variable_definitions() == []


def test_list_variable_definitions_with_date_of_validity(
    client_configuration: Configuration,
):
    Vardef.set_config(client_configuration)
    assert isinstance(
        Vardef.list_variable_definitions(date_of_validity=VARDEF_EXAMPLE_DATE)[0],
        CompleteResponse,
    )


def test_get_variable_definition(client_configuration: Configuration):
    Vardef.set_config(client_configuration)
    assert Vardef.get_variable_definition(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
