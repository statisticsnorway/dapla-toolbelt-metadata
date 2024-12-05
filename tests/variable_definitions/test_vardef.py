from dapla_metadata.variable_definitions.generated.vardef_client.models.complete_response import (
    CompleteResponse,
)
from dapla_metadata.variable_definitions.vardef import Vardef
from tests.utils.constants import VARDEF_EXAMPLE_DATE


def test_list(client_configuration):
    Vardef.set_config(client_configuration)
    assert Vardef.list_variable_definitions() == []


def test_list_with_date_of_validity(client_configuration):
    Vardef.set_config(client_configuration)
    assert isinstance(
        Vardef.list_variable_definitions(date_of_validity=VARDEF_EXAMPLE_DATE)[0],
        CompleteResponse,
    )
