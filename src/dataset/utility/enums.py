"""Enumerations used in Datadoc."""

from __future__ import annotations

from enum import Enum

from datadoc_model import model
from datadoc_model.model import LanguageStringType
from datadoc_model.model import LanguageStringTypeItem


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


class LanguageStringsEnum(Enum):
    """Enum class for storing LanguageStringType objects."""

    def __init__(
        self,
        language_strings: LanguageStringType,
    ) -> None:
        """Store the LanguageStringType object for displaying enum values in multiple languages.

        We don't particularly care what the value of the enum is,
        but when serialised it's convenient and readable to use the
        name of the enum, so we set the value to be the name.
        """
        self._value_ = self.name
        self.language_strings = language_strings

    def get_value_for_language(
        self,
        language: SupportedLanguages,
    ) -> str | None:
        """Retrieve the string for the relevant language."""
        if self.language_strings.root is not None:
            for item in self.language_strings.root:
                if item.languageCode == language:
                    return item.languageText
        return None


class DataSetState(LanguageStringsEnum):
    """Processing state of a dataset."""

    SOURCE_DATA = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataSetState.SOURCE_DATA.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="KILDEDATA"),
            LanguageStringTypeItem(languageCode="nb", languageText="KILDEDATA"),
        ],
    )
    INPUT_DATA = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataSetState.INPUT_DATA.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="INNDATA"),
            LanguageStringTypeItem(languageCode="nb", languageText="INNDATA"),
        ],
    )
    PROCESSED_DATA = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataSetState.PROCESSED_DATA.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="KLARGJORTE DATA"),
            LanguageStringTypeItem(languageCode="nb", languageText="KLARGJORTE DATA"),
        ],
    )
    STATISTICS = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataSetState.STATISTICS.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="STATISTIKK"),
            LanguageStringTypeItem(languageCode="nb", languageText="STATISTIKK"),
        ],
    )
    OUTPUT_DATA = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataSetState.OUTPUT_DATA.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="UTDATA"),
            LanguageStringTypeItem(languageCode="nb", languageText="UTDATA"),
        ],
    )
