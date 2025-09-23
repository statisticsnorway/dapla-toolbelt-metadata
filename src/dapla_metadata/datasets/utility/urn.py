"""Validate, parse and render URNs."""

import re
from dataclasses import dataclass
from enum import Enum
from enum import auto


class ReferenceUrlTypes(Enum):
    API_TEST = auto()
    API_PROD = auto()
    FRONTEND_TEST = auto()
    FRONTEND_PROD = auto()


@dataclass
class UrnConverter:
    urn_base: str
    url_base_patterns: dict[ReferenceUrlTypes, re.Pattern[str]]

    def extract_id(self, unvalidated: str, pattern: re.Pattern[str]) -> str | None:
        if match := pattern.match(unvalidated):
            return match.group(1)
        return None

    def convert_to_urn(self, unvalidated: str | None) -> str | None:
        if not unvalidated:
            return None

        my_id = next(
            self.extract_id(unvalidated, pattern)
            for pattern in self.url_base_patterns.values()
        )
        if my_id:
            return f"{self.urn_base}:{my_id}"

        return None


vardef_urn_converter = UrnConverter(
    urn_base="urn:ssb:variable-definition:vardef",
    url_base_patterns={
        ReferenceUrlTypes.API_PROD: re.compile(
            "^https://metadata.ssb.no/variable-definitions/([a-z0-9]{8})"
        )
    },
)
