VARDEF_EXAMPLE_DEFINITION_ID = "wypvb3wd"
VARDEF_EXAMPLE_ACTIVE_GROUP = "dapla-felles-developers"
VARDEF_EXAMPLE_DATE = "1970-01-01"
JUPYTERHUB_USER = "JUPYTERHUB_USER"
DAPLA_REGION = "DAPLA_REGION"
DAPLA_GROUP_CONTEXT = "DAPLA_GROUP_CONTEXT"
DAPLA_SERVICE = "DAPLA_SERVICE"
NOT_FOUND_STATUS = 404
BAD_REQUEST_STATUS = 400
CONSTRAINT_VIOLATION_BODY = """{
    "cause": null,
    "suppressed": [
    ],
    "detail": null,
    "instance": null,
    "parameters": {
    },
    "type": "https://zalando.github.io/problem/constraint-violation",
    "title": "Constraint Violation",
    "status": 400,
    "violations": [
        {
            "field": "updateVariableDefinitionById.updateDraft.owner.team",
            "message": "Invalid Dapla team"
        },
        {
            "field": "updateVariableDefinitionById.updateDraft.owner.team",
            "message": "must not be empty"
        }
    ]
}"""
