from pydantic import ConfigDict

from dapla_metadata.variable_definitions.generated.vardef_client.models.complete_response import (
    CompleteResponse,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.contact import (
    Contact,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.language_string_type import (
    LanguageStringType,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.owner import (
    Owner,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.variable_status import (
    VariableStatus,
)
from dapla_metadata.variable_definitions.utils.constants import DEFAULT_DATE


class CompletePatchOutput(CompleteResponse):
    """Complete response For internal users who need all details while maintaining variable definitions."""

    @staticmethod
    def from_model(
        model: CompleteResponse,
    ) -> "CompletePatchOutput":
        """Create a CompletePatchOutput instance from a CompleteResponse."""
        return CompletePatchOutput.model_construct(**model.model_dump())

    model_config = ConfigDict(use_enum_values=True, str_strip_whitespace=True)

    def to_dict(self) -> dict:
        """Return as dictionary."""
        return super().to_dict()

    def __str__(self) -> str:
        """Format as indented JSON."""
        i = self.model_dump(
            mode="json",
            serialize_as_any=True,
            warnings="error",
        )

        import yaml

        yaml_str = yaml.dump(
            i,
            allow_unicode=True,
            default_flow_style=False,
        )
        return yaml_str  # self.model_dump_json(indent=2, warnings=False)


DEFAULT_TEMPLATE = CompletePatchOutput(
    name=LanguageStringType(nb="default navn", nn="default namn", en="default name"),
    short_name="default_kortnavn",
    definition=LanguageStringType(
        nb="default definisjon",
        nn="default definisjon",
        en="default definition",
    ),
    classification_reference="class_id",
    valid_from=DEFAULT_DATE,
    unit_types=["00"],
    subject_fields=["aa"],
    contains_special_categories_of_personal_data=False,
    variable_status=VariableStatus.DRAFT.value,
    owner=Owner(team="default team", groups=["default group"]),
    contact=Contact(
        title=LanguageStringType(
            nb="default tittel",
            nn="default tittel",
            en="default title",
        ),
        email="default@ssb.no",
    ),
    id="",
    patch_id=0,
    created_at=DEFAULT_DATE,
    created_by="",
    last_updated_at=DEFAULT_DATE,
    last_updated_by="",
)
