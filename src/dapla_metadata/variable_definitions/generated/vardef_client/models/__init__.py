# coding: utf-8

# flake8: noqa
"""
Variable Definitions

## Introduction  Variable Definitions are centralized definitions of concrete variables which are typically present in multiple datasets. Variable Definitions support standardization of data and metadata and facilitate sharing and joining of data by clarifying when variables have an identical definition.  ## Maintenance of Variable Definitions This API allows for creation, maintenance and access of Variable Definitions.  ### Ownership Creation and maintenance of variables may only be performed by Statistics Norway employees representing a specific Dapla team, who are defined as the owners of a given Variable Definition. The team an owner represents must be specified when making a request through the `active_group` query parameter. All maintenance is to be performed by the owners, with no intervention from administrators.  ### Status All Variable Definitions have an associated status. The possible values for status are `DRAFT`, `PUBLISHED_INTERNAL` and `PUBLISHED_EXTERNAL`.   #### Draft When a Variable Definition is created it is assigned the status `DRAFT`. Under this status the Variable Definition is:  - Only visible to Statistics Norway employees. - Mutable (it may be changed directly without need for versioning). - Not suitable to refer to from other systems.  This status may be changed to `PUBLISHED_INTERNAL` or `PUBLISHED_EXTERNAL` with a direct update.  #### Published Internal Under this status the Variable Definition is:  - Only visible to Statistics Norway employees. - Immutable (all changes are versioned). - Suitable to refer to in internal systems for statistics production. - Not suitable to refer to for external use (for example in Statistikkbanken).  This status may be changed to `PUBLISHED_EXTERNAL` by creating a Patch version.  #### Published External Under this status the Variable Definition is:  - Visible to the general public. - Immutable (all changes are versioned). - Suitable to refer to from any system.  This status may not be changed as it would break immutability. If a Variable Definition is no longer relevant then its period of validity should be ended by specifying a `valid_until` date in a Patch version.  ### Immutability Variable Definitions are immutable. This means that any changes must be performed in a strict versioning system. Consumers can avoid being exposed to breaking changes by specifying a `date_of_validity` when they request a Variable Definition.  #### Patches Patches are for changes which do not affect the fundamental meaning of the Variable Definition.  #### Validity Periods Validity Periods are versions with a period defined by a `valid_from` date and optionally a `valid_until` date. If the fundamental meaning of a Variable Definition is to be changed, it should be done by creating a new Validity Period.

The version of the OpenAPI document: 0.1
Contact: metadata@ssb.no
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

# import models into model package
from ..models.complete_response import CompleteResponse
from ..models.contact import Contact
from ..models.draft import Draft
from ..models.klass_reference import KlassReference
from ..models.language_string_type import LanguageStringType
from ..models.owner import Owner
from ..models.patch import Patch
from ..models.person import Person
from ..models.rendered_contact import RenderedContact
from ..models.rendered_variable_definition import RenderedVariableDefinition
from ..models.supported_languages import SupportedLanguages
from ..models.update_draft import UpdateDraft
from ..models.validity_period import ValidityPeriod
from ..models.variable_status import VariableStatus