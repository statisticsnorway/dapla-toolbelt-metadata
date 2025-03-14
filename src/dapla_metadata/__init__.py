"""Tools and clients for working with the Dapla Metadata system."""

import warnings

warnings.filterwarnings(
    "ignore",
    message="As the c extension couldn't be imported, `google-crc32c` is using a pure python implementation that is significantly slower.",
)

import datadoc_model.model as datadoc_model

from . import datasets
from . import variable_definitions
