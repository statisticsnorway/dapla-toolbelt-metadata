import pytest

from dapla_metadata.dapla.name_validator import _is_invalid_symbols


@pytest.mark.parametrize(
    ("data", "expected_result"),
    [
        (
            "buckets/ssb-dapla-example-data-produkt-prod/ledstill/utdata/persån_testdata_p2021-12-31_p2021-12-31_v1.parquet",
            True,
        ),
        (
            "buckets/ssb-dapla-example-data-produkt-prod/ledstill/utdata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
            False,
        ),
        (
            "ssb-dapla-example-data-produkt-prod/ledstill/oppdrag/skjema_p2018_p2020_v1",
            False,
        ),
        (
            "ssbÆ-dapla-example-data-produkt-prod/ledstill/oppdrag/skjema_p2018_p2020_v1",
            True,
        ),
    ],
)
def test_symbols_in_filepath(data: str, expected_result: bool):
    assert _is_invalid_symbols(data) == expected_result
