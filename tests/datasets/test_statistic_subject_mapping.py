import pytest
import requests
from bs4 import BeautifulSoup

from dapla_metadata.datasets.statistic_subject_mapping import PrimarySubject
from dapla_metadata.datasets.statistic_subject_mapping import SecondarySubject
from dapla_metadata.datasets.statistic_subject_mapping import StatisticSubjectMapping
from tests.datasets.constants import TEST_RESOURCES_DIRECTORY


def test_no_source_url(thread_pool_executor):
    subject_mapping = StatisticSubjectMapping(thread_pool_executor, None)
    subject_mapping.wait_for_external_result()
    assert subject_mapping.primary_subjects == []


def test_extract_titles():
    xml_string = '<titler><tittel sprak="no">Partifinansiering</tittel><tittel sprak="en">Funding of political parties</tittel></titler>'
    soup = BeautifulSoup(xml_string, features="xml")
    assert StatisticSubjectMapping._extract_titles(soup) == {  # noqa: SLF001
        "no": "Partifinansiering",
        "en": "Funding of political parties",
    }


STATISTICAL_SUBJECT_STRUCTURE_DIR = "statistical_subject_structure"


@pytest.mark.parametrize(
    ("subject_xml_file_path", "expected"),
    [
        (
            TEST_RESOURCES_DIRECTORY / STATISTICAL_SUBJECT_STRUCTURE_DIR / "simple.xml",
            [
                PrimarySubject(
                    titles={"en": "aa english", "no": "aa norwegian"},
                    subject_code="aa",
                    secondary_subjects=[
                        SecondarySubject(
                            titles={"en": "aa00 english", "no": "aa00 norwegian"},
                            subject_code="aa00",
                            statistic_short_names=["aa_kortnvan"],
                        ),
                    ],
                ),
            ],
        ),
        (
            TEST_RESOURCES_DIRECTORY / STATISTICAL_SUBJECT_STRUCTURE_DIR / "empty.xml",
            [],
        ),
        (
            TEST_RESOURCES_DIRECTORY
            / STATISTICAL_SUBJECT_STRUCTURE_DIR
            / "missing_language.xml",
            [
                PrimarySubject(
                    titles={
                        "en": "aa english",
                    },
                    subject_code="aa",
                    secondary_subjects=[
                        SecondarySubject(
                            titles={
                                "no": "aa00 norwegian",
                                "en": "aa00 english",
                            },
                            subject_code="aa00",
                            statistic_short_names=["aa_kortnvan"],
                        ),
                        SecondarySubject(
                            titles={
                                "no": "aa01 norwegian",
                            },
                            subject_code="aa01",
                            statistic_short_names=["aa_kortnvan_01"],
                        ),
                    ],
                ),
                PrimarySubject(
                    titles={
                        "en": "ab english",
                    },
                    subject_code="ab",
                    secondary_subjects=[
                        SecondarySubject(
                            titles={
                                "no": "ab00 norwegian",
                                "en": "ab00 english",
                            },
                            subject_code="ab00",
                            statistic_short_names=["ab_kortnvan"],
                        ),
                        SecondarySubject(
                            titles={
                                "en": "ab01 english",
                            },
                            subject_code="ab01",
                            statistic_short_names=["ab_kortnvan_01"],
                        ),
                    ],
                ),
            ],
        ),
    ],
)
@pytest.mark.usefixtures("_mock_fetch_statistical_structure")
def test_read_in_statistical_structure(
    subject_mapping_fake_statistical_structure: StatisticSubjectMapping,
    expected: list[PrimarySubject],
) -> None:
    subject_mapping_fake_statistical_structure.wait_for_external_result()
    assert subject_mapping_fake_statistical_structure.primary_subjects == expected


@pytest.mark.parametrize(
    ("statistic_short_name", "expected_secondary_subject"),
    [
        ("ab_kortnvan", "ab00"),
        ("aa_kortnvan", "aa00"),
        ("ab_kortnvan_01", "ab01"),
        ("aa_kortnvan_01", "aa01"),
        ("unknown_name", None),
        (None, None),
    ],
)
@pytest.mark.usefixtures("_mock_fetch_statistical_structure")
def test_get_secondary_subject(
    subject_mapping_fake_statistical_structure: StatisticSubjectMapping,
    statistic_short_name: str,
    expected_secondary_subject: str,
) -> None:
    subject_mapping_fake_statistical_structure.wait_for_external_result()
    assert (
        subject_mapping_fake_statistical_structure.get_secondary_subject(
            statistic_short_name,
        )
        == expected_secondary_subject
    )


@pytest.fixture
def subject_mapping_http_exception(
    requests_mock,
    exception_to_raise,
    thread_pool_executor,
) -> StatisticSubjectMapping:
    requests_mock.get(
        "http://test.some.url.com",
        exc=exception_to_raise,
    )
    return StatisticSubjectMapping(thread_pool_executor, "http://test.some.url.com")


@pytest.mark.parametrize(
    ("exception_to_raise"),
    [
        (requests.exceptions.ConnectTimeout),
        (requests.exceptions.HTTPError),
        (requests.exceptions.ReadTimeout),
        (requests.exceptions.ConnectionError),
    ],
)
def test_subject_mapping_http_exception(
    subject_mapping_http_exception: StatisticSubjectMapping,
) -> None:
    subject_mapping_http_exception.wait_for_external_result()
    assert subject_mapping_http_exception.primary_subjects == []
