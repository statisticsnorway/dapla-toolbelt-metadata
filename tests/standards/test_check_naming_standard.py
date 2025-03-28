import pytest

from dapla_metadata.standards.standard_validators import check_naming_standard

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_check_naming_standard():
    results = await check_naming_standard(
        "gs://ssb-dapla-felles-data-produkt-test",
    )
    print(results)
    assert len(results) > 0
