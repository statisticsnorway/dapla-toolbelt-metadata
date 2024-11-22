from dapla_metadata.variable_definitions.generated import vardef_client


def test_create_draft(api_client, draft):
    api_instance = vardef_client.DraftVariableDefinitionsApi(api_client)
    active_group = "dapla-felles-developers"
    api_instance.create_variable_definition(active_group, draft)
