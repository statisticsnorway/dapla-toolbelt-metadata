from dapla_metadata.variable_definitions.utils.translations import (
    apply_translations_to_model,
)
from dapla_metadata.variable_definitions.variable_definition import CompletePatchOutput


def test_descriptions():
    apply_translations_to_model(CompletePatchOutput)
    field_metadata = CompletePatchOutput.model_fields["name"]
    assert (
        field_metadata.json_schema_extra["translated_description"]
        == "Variabelens navn. Dette skal ikke være en mer “teknisk” forkortelse, men et navn som er forståelig for mennesker, f.eks. “Lønnsinntekter”."
    )
