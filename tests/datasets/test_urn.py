import logging

import datadoc_model.all_optional.model as all_optional_model
import pytest

from dapla_metadata.datasets.core import Datadoc
from dapla_metadata.datasets.utility.urn import SsbNaisDomains
from dapla_metadata.datasets.utility.urn import vardef_urn_converter

VARIABLE_DEFINITION_URN_TEST_CASES = [
    (None, None),
    *[
        (
            f"https://metadata.{domain.value}/variable-definitions/hd8sks89",
            "urn:ssb:variable-definition:vardef:hd8sks89",
        )
        for domain in SsbNaisDomains
    ],
    *[
        (
            f"https://catalog.{domain.value}/variable-definitions/hd8sks89",
            "urn:ssb:variable-definition:vardef:hd8sks89",
        )
        for domain in SsbNaisDomains
    ],
]


@pytest.mark.parametrize(
    ("case", "expected_result"),
    [
        *VARIABLE_DEFINITION_URN_TEST_CASES,
        (
            "https://www.vg.no",
            None,
        ),
    ],
)
def test_convert_to_vardef_urn(case: str | None, expected_result: str | None):
    assert vardef_urn_converter.convert_to_urn(case) == expected_result


@pytest.mark.parametrize(
    ("case", "expected_result"),
    [
        *VARIABLE_DEFINITION_URN_TEST_CASES,
        (
            "https://www.vg.no",
            "https://www.vg.no/",
        ),
    ],
)
def test_convert_to_vardef_urn_end_to_end(
    case: str | None, expected_result: str | None, caplog
):
    caplog.set_level(logging.ERROR)
    meta = Datadoc()
    meta._set_metadata(  # noqa: SLF001
        all_optional_model.DatadocMetadata(
            dataset=all_optional_model.Dataset(),
            variables=[all_optional_model.Variable(definition_uri=case)],
        )
    )
    if not expected_result:
        assert meta.variables[0].definition_uri is None
    else:
        assert str(meta.variables[0].definition_uri) == expected_result
        if not expected_result.startswith("urn:"):
            assert "Could not convert value to URN" in caplog.text
