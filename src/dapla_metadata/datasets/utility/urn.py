"""Validate, parse and render URNs."""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from enum import auto

from pydantic import AnyUrl

from dapla_metadata.datasets.utility.utils import VariableListType

logger = logging.getLogger(__name__)


VARDEF_URL_TEMPLATE = "https://{subdomain}.{domain}/variable-definitions"


class SsbNaisDomains(str, Enum):
    """The available domains on SSBs Nais instance."""

    TEST_EXTERNAL = "test.ssb.no"
    TEST_INTERNAL = "intern.test.ssb.no"
    PROD_EXTERNAL = "ssb.no"
    PROD_INTERNAL = "intern.ssb.no"


class ReferenceUrlTypes(Enum):
    """The general category of the URL.

    This can be useful to refer to when constructing a URL from a URN for a
    specific context.
    """

    API = auto()
    FRONTEND = auto()


@dataclass
class UrnConverter:
    """Converts URLs to URNs and vice versa.

    Fields:
        urn_base: The format for the URN, up to the identifier.
        id_pattern: A capturing group pattern which matches identifiers for this resource.
        url_bases: The list of all the different URL representations for a resource. There
            will typically be a number of URL representations for a particular resource,
            depending on which system or technology they are accessed through and other
            technical factors. This list defines which concrete URLs can be considered
            equivalent to a URN.
    """

    urn_base: str
    id_pattern: str
    url_bases: list[tuple[ReferenceUrlTypes, str]]

    def _extract_id(self, url: str, pattern: re.Pattern[str]) -> str | None:
        if match := pattern.match(url):
            return match.group(1)
        return None

    def _build_pattern(self, url_base: str) -> re.Pattern[str]:
        return re.compile(f"^{url_base}/{self.id_pattern}")

    def build_urn(self, identifier: str) -> str:
        """Build a URN for the given identifier."""
        return f"{self.urn_base}:{identifier}"

    def convert_to_urn(self, url: str | AnyUrl | None) -> str | None:
        """Convert a URL to a generalized URN for that same resource.

        Args:
            url (str | None): The URL to convert.

        Returns:
            str | None: The URN or None if it can't be converted.
        """
        if not url:
            return None

        patterns = (self._build_pattern(url[-1]) for url in self.url_bases)
        matches = (self._extract_id(str(url), p) for p in patterns)
        identifier = next((m for m in matches if m), None)
        if identifier:
            return self.build_urn(identifier)

        return None


vardef_urn_converter = UrnConverter(
    urn_base="urn:ssb:variable-definition:vardef",
    id_pattern=r"([a-z0-9]{8})",
    url_bases=[
        *[
            (
                ReferenceUrlTypes.API,
                VARDEF_URL_TEMPLATE.format(
                    subdomain="metadata", domain=nais_domain.value
                ),
            )
            for nais_domain in SsbNaisDomains
        ],
        *[
            (
                ReferenceUrlTypes.FRONTEND,
                VARDEF_URL_TEMPLATE.format(
                    subdomain="catalog", domain=nais_domain.value
                ),
            )
            for nais_domain in SsbNaisDomains
        ],
    ],
)


def convert_definition_uris_to_urns(variables: VariableListType) -> None:
    """Where definition URIs are recognized URLs, convert them to URNs.

    Where the value is not a known URL we preserve the value as it is and log an
    ERROR level message.

    Args:
        variables (VariableListType): The list of variables.
    """
    for v in variables:
        if urn := vardef_urn_converter.convert_to_urn(v.definition_uri):
            v.definition_uri = urn  # type: ignore [assignment]
        else:
            logger.error("Could not convert value to URN: %s", v.definition_uri)
