"""Client for working with Variable Definitions at Statistics Norway."""

from .generated.vardef_client import models
from .generated.vardef_client.exceptions import *  # noqa: F403
from .vardef import Vardef
from .variable_definition import CompletePatchOutput
from .variable_definition import VariableDefinition
