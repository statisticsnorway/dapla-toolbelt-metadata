import pytest

from dapla_metadata.datasets.utility.urn import vardef_urn_converter


@pytest.mark.parametrize(
    ("case", "expected_result"),
    [
        (None, None),
        (
            "https://metadata.ssb.no/variable-definitions/hd8sks89",
            "urn:ssb:variable-definition:vardef:hd8sks89",
        ),
        (
            "https://catalog.ssb.no/variable-definitions/hd8sks89",
            "urn:ssb:variable-definition:vardef:hd8sks89",
        ),
        (
            "https://www.vg.no",
            None,
        ),
    ],
)
def test_convert_to_vardef_urn(case: str | None, expected_result: str | None):
    assert vardef_urn_converter.convert_to_urn(case) == expected_result
