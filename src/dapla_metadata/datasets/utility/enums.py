"""Enumerations used in Datadoc."""

from enum import StrEnum


class SupportedLanguages(StrEnum):
    """The list of languages metadata may be recorded in.

    Reference: https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry
    """

    NORSK_BOKMÅL = "nb"  # noqa: PLC2401 the listed problems do not apply in this case
    NORSK_NYNORSK = "nn"
    ENGLISH = "en"


class EncryptionAlgorithm(StrEnum):
    """Encryption algorithm values for pseudonymization algoprithms offered on Dapla."""

    PAPIS_ENCRYPTION_ALGORITHM = "TINK-FPE"
    DAEAD_ENCRYPTION_ALGORITHM = "TINK-DAEAD"
