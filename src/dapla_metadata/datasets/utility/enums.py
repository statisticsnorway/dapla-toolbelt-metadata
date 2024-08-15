"""Enumerations used in Datadoc."""

from __future__ import annotations

from enum import Enum


class DaplaRegion(str, Enum):
    """Dapla platforms/regions."""

    DAPLA_LAB = "DAPLA_LAB"
    BIP = "BIP"
    ON_PREM = "ON_PREM"
    CLOUD_RUN = "CLOUD_RUN"


class DaplaService(str, Enum):
    """Dapla services."""

    DATADOC = "DATADOC"
    JUPYTERLAB = "JUPYTERLAB"
    VS_CODE = "VS_CODE"
    R_STUDIO = "R_STUDIO"
    KILDOMATEN = "KILDOMATEN"


class SupportedLanguages(str, Enum):
    """The list of languages metadata may be recorded in.

    Reference: https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry
    """

    NORSK_BOKMÅL = "nb"
    NORSK_NYNORSK = "nn"
    ENGLISH = "en"
