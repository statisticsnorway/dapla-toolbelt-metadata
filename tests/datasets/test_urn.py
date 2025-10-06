import logging

import datadoc_model.all_optional.model as all_optional_model
import pytest

from dapla_metadata.datasets.core import Datadoc
from dapla_metadata.datasets.utility.urn import SsbNaisDomains
from dapla_metadata.datasets.utility.urn import klass_urn_converter
from dapla_metadata.datasets.utility.urn import vardef_urn_converter

VARIABLE_DEFINITION_URN_TEST_CASES = [
    *[
        (
            f"https://metadata.{domain.value}/variable-definitions/hd8sks89",
            "urn:ssb:variable-definition:vardef:hd8sks89",
            False,
        )
        for domain in SsbNaisDomains
    ],
    *[
        (
            f"https://catalog.{domain.value}/variable-definitions/hd8sks89",
            "urn:ssb:variable-definition:vardef:hd8sks89",
            False,
        )
        for domain in SsbNaisDomains
    ],
]


@pytest.mark.parametrize(
    ("case", "expected_result", "expect_warning"),
    [
        *VARIABLE_DEFINITION_URN_TEST_CASES,
        ("https://www.vg.no", None, True),
    ],
)
def test_convert_to_vardef_urn(
    case: str,
    expected_result: str | None,
    expect_warning: bool,  # noqa: ARG001
):
    assert vardef_urn_converter.convert_to_urn(case) == expected_result


@pytest.mark.parametrize(
    ("case", "expected_result", "expect_warning"),
    [
        *VARIABLE_DEFINITION_URN_TEST_CASES,
        ("https://www.vg.no", "https://www.vg.no/", True),
        (None, None, False),
    ],
)
def test_convert_to_vardef_urn_end_to_end(
    case: str | None,
    expected_result: str | None,
    expect_warning: bool,
    caplog: pytest.LogCaptureFixture,
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
    assert ("Could not convert value to URN" in caplog.text) is expect_warning


CLASSIFICATION_URN_TEST_CASES = [
    (
        "https://www.ssb.no/klass/klassifikasjoner/91",
        "urn:ssb:classification:klass:91",
        False,
    ),
    (
        "https://www.ssb.no/en/klass/klassifikasjoner/91",
        "urn:ssb:classification:klass:91",
        False,
    ),
    (
        "https://data.ssb.no/api/klass/v1/classifications/91",
        "urn:ssb:classification:klass:91",
        False,
    ),
    (
        "https://data.ssb.no/api/klass/v1/classifications/91.json",
        "urn:ssb:classification:klass:91",
        False,
    ),
]


@pytest.mark.parametrize(
    ("case", "expected_result", "expect_warning"),
    CLASSIFICATION_URN_TEST_CASES,
)
def test_convert_to_klass_urn(
    case: str,
    expected_result: str | None,
    expect_warning: bool,  # noqa: ARG001
):
    assert klass_urn_converter.convert_to_urn(case) == expected_result


@pytest.mark.parametrize(
    ("case", "expected_result", "expect_warning"),
    [
        *CLASSIFICATION_URN_TEST_CASES,
        ("https://www.vg.no", "https://www.vg.no/", True),
        (None, None, False),
    ],
)
def test_convert_to_klass_urn_end_to_end(
    case: str | None,
    expected_result: str | None,
    expect_warning: bool,
    caplog: pytest.LogCaptureFixture,
):
    caplog.set_level(logging.ERROR)
    meta = Datadoc()
    meta._set_metadata(  # noqa: SLF001
        all_optional_model.DatadocMetadata(
            dataset=all_optional_model.Dataset(),
            variables=[all_optional_model.Variable(classification_uri=case)],
        )
    )
    if not expected_result:
        assert meta.variables[0].classification_uri is None
    else:
        assert str(meta.variables[0].classification_uri) == expected_result
    assert ("Could not convert value to URN" in caplog.text) is expect_warning
