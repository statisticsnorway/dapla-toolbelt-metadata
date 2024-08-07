import pytest
from src.dataset.utility.enums import SupportedLanguages

from dataset.code_list import CodeList
from tests.dataset.constants import TEST_RESOURCES_DIRECTORY

CODE_LIST_DIR = "code_list"


@pytest.mark.parametrize(
    (
        "code_list_csv_filepath_nb",
        "code_list_csv_filepath_nn",
        "code_list_csv_filepath_en",
        "titles",
        "codes",
    ),
    [
        (
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "code_list_nb.csv",
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "code_list_nn.csv",
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "code_list_en.csv",
            ["Adresse", "Arbeidsulykke", "Bolig"],
            ["01", "02", "03"],
        ),
        (
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "no_code.csv",
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "no_code.csv",
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "no_code.csv",
            ["Adresse", "Arbeidsulykke", "Bolig"],
            [None, None, None],
        ),
    ],
)
@pytest.mark.usefixtures("_mock_fetch_dataframe")
def test_read_dataframe(
    code_list_fake_structure: CodeList,
    codes: list[str],
    titles: list[str],
):
    code_list_fake_structure.wait_for_external_result()

    for i in range(3):
        assert code_list_fake_structure.classifications[i].code == codes[i]

    assert all(
        code_list_fake_structure.classifications[i].titles[language] == titles[i]
        for i in range(3)
        for language in SupportedLanguages
    )


def test_non_existent_code(thread_pool_executor):
    code_list = CodeList(thread_pool_executor, 0)
    code_list.wait_for_external_result()
    assert code_list.classifications == []
