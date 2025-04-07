from pathlib import Path
from typing import TYPE_CHECKING

from dapla_metadata.variable_definitions._generated.vardef_client.models.complete_response import (
    CompleteResponse,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.contact import (
    Contact,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.language_string_type import (
    LanguageStringType,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.owner import (
    Owner,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.variable_status import (
    VariableStatus,
)
from dapla_metadata.variable_definitions._utils.constants import DEFAULT_DATE
from dapla_metadata.variable_definitions._utils.constants import TEMPLATE_HEADER
from dapla_metadata.variable_definitions._utils.files import _create_file_name
from dapla_metadata.variable_definitions._utils.files import _get_current_time
from dapla_metadata.variable_definitions._utils.files import (
    _get_variable_definitions_dir,
)
from dapla_metadata.variable_definitions._utils.files import (
    _model_to_yaml_with_comments,
)
from dapla_metadata.variable_definitions._utils.files import logger

if TYPE_CHECKING:
    from dapla_metadata.variable_definitions.variable_definition import (
        VariableDefinition,
    )


def _get_default_template() -> "VariableDefinition":
    from dapla_metadata.variable_definitions.variable_definition import (
        VariableDefinition,
    )

    return VariableDefinition(
        name=LanguageStringType(
            nb="Skriv 'navn' på norsk bokmål. Fjern språk og verdier du ikke vil lagre",
            nn="Skriv 'namn' på nynorsk. Fjern språk og verdiar du ikkje vil lagre",
            en="Write 'name' in english. Remove language and values you do not want to save",
        ),
        short_name="generert_kortnavn",
        definition=LanguageStringType(
            nb="Her kan du skrive definisjonsteksten på norsk bokmål. Dette er kun en placeholder og må fjernes eller endres før du oppretter en ny variabeldefinisjon.",
            nn="Her kan du skrive definisjonsteksten på nynorsk. Dette er berre ein placeholder og må fjernast eller endrast før du opprettar ein ny variabeldefinisjon.",
            en="Here you can write the definition text in English. This is just a placeholder and must be removed or changed before you create a new variable definition.",
        ),
        valid_from=DEFAULT_DATE,
        unit_types=[""],
        subject_fields=[""],
        contains_special_categories_of_personal_data=False,
        variable_status=VariableStatus.DRAFT.value,
        owner=Owner(team="default team", groups=["default group"]),
        contact=Contact(
            title=LanguageStringType(
                nb="Skriv tittel på kontakt norsk bokmål. Fjern språk og verdier du ikke vil lagre",
                nn="Skriv tittel på kontakt norsk nynorsk. Fjern språk og verdiar du ikkje vil lagre",
                en="Write title for contact in english. Remove language and values you do not want to save",
            ),
            email="generert@ssb.no",
        ),
        id="",
        patch_id=0,
        created_at=DEFAULT_DATE,
        created_by="",
        last_updated_at=DEFAULT_DATE,
        last_updated_by="",
    )


def create_template_yaml(
    model_instance: CompleteResponse | None = None,
    custom_directory: Path | None = None,
) -> Path:
    """Creates a template yaml file for a new variable definition."""
    if model_instance is None:
        model_instance = _get_default_template()
    file_name = _create_file_name(
        "variable_definition_template",
        _get_current_time(),
    )

    file_path = _model_to_yaml_with_comments(
        model_instance,
        file_name,
        TEMPLATE_HEADER,
        custom_directory=custom_directory,
    )
    logger.debug("Created %s", file_path)
    return file_path


def _find_latest_template_file(directory: Path | None = None) -> Path | None:
    def _filter_template_file(path: Path) -> bool:
        return "variable_definition_template" in path.stem and path.suffix == ".yaml"

    try:
        return sorted(
            filter(
                _filter_template_file,
                (directory or _get_variable_definitions_dir()).iterdir(),
            ),
        )[-1]
    except IndexError:
        return None
