"""Tests for pseudonymization."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from typing import TYPE_CHECKING

import pytest
from datadoc_model.all_optional.model import Pseudonymization

from dapla_metadata.datasets.utility.constants import DAED_ENCRYPTION_KEY_REFERENCE
from dapla_metadata.datasets.utility.constants import PAPIS_ENCRYPTION_KEY_REFERENCE
from dapla_metadata.datasets.utility.constants import (
    PAPIS_ENCRYPTION_PARAMETER_STRATEGY,
)
from dapla_metadata.datasets.utility.constants import (
    PAPIS_ENCRYPTION_PARAMETER_STRATEGY_SKIP,
)
from dapla_metadata.datasets.utility.constants import PAPIS_STABLE_IDENTIFIER_TYPE
from dapla_metadata.datasets.utility.constants import (
    PAPIS_WITH_STABLE_ID_ENCRYPTION_PARAMETER_SNAPSHOT_DATE,
)
from dapla_metadata.datasets.utility.enums import EncryptionAlgorithm
from dapla_metadata.datasets.utility.utils import get_current_date
from tests.datasets.constants import TEST_PSEUDO_DIRECTORY

if TYPE_CHECKING:
    from datetime import datetime  # noqa: TC004
    from pathlib import Path

    from dapla_metadata.datasets.core import Datadoc


@dataclass
class PseudoCase:
    existing_pseudo: Pseudonymization | None = None
    new_pseudo: Pseudonymization | None = None
    expected_algorithm: str | None = None
    expected_stable_type: str | None = None
    expected_key: str | None = None
    expected_params: list[dict] | None = None
    expected_pseudo_time: datetime | None = None
    expected_stable_version: str | None = None


def _assert_dicts_in_list(expected: list[dict] | None, actual: list[dict]):
    if expected:
        for d in expected:
            assert d in actual, f"Missing expected dict: {d}"


@pytest.mark.parametrize(
    "case",
    [
        PseudoCase(
            existing_pseudo=None,
            new_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            ),
            expected_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            expected_key=PAPIS_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {"keyId": PAPIS_ENCRYPTION_KEY_REFERENCE},
                {
                    PAPIS_ENCRYPTION_PARAMETER_STRATEGY: PAPIS_ENCRYPTION_PARAMETER_STRATEGY_SKIP
                },
            ],
            expected_pseudo_time=None,
        ),
        PseudoCase(
            existing_pseudo=Pseudonymization(),
            new_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            ),
            expected_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            expected_key=PAPIS_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {"keyId": PAPIS_ENCRYPTION_KEY_REFERENCE},
                {
                    PAPIS_ENCRYPTION_PARAMETER_STRATEGY: PAPIS_ENCRYPTION_PARAMETER_STRATEGY_SKIP
                },
            ],
            expected_pseudo_time=None,
        ),
        PseudoCase(
            existing_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            ),
            new_pseudo=None,
            expected_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            expected_key=None,
            expected_params=None,
            expected_pseudo_time=None,
        ),
        PseudoCase(
            existing_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
                encryption_key_reference=PAPIS_ENCRYPTION_KEY_REFERENCE,
                encryption_algorithm_parameters=[
                    {"keyId": PAPIS_ENCRYPTION_KEY_REFERENCE},
                    {
                        PAPIS_ENCRYPTION_PARAMETER_STRATEGY: PAPIS_ENCRYPTION_PARAMETER_STRATEGY_SKIP
                    },
                ],
            ),
            new_pseudo=Pseudonymization(
                pseudonymization_time=datetime(
                    2018, 3, 3, 12, 30, 0, tzinfo=timezone.utc
                ),
            ),
            expected_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            expected_key=PAPIS_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {"keyId": PAPIS_ENCRYPTION_KEY_REFERENCE},
                {
                    PAPIS_ENCRYPTION_PARAMETER_STRATEGY: PAPIS_ENCRYPTION_PARAMETER_STRATEGY_SKIP
                },
            ],
            expected_pseudo_time=datetime(2018, 3, 3, 12, 30, 0, tzinfo=timezone.utc),
        ),
        PseudoCase(
            existing_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
                encryption_key_reference=PAPIS_ENCRYPTION_KEY_REFERENCE,
                encryption_algorithm_parameters=[
                    {"keyId": PAPIS_ENCRYPTION_KEY_REFERENCE},
                    {
                        PAPIS_ENCRYPTION_PARAMETER_STRATEGY: PAPIS_ENCRYPTION_PARAMETER_STRATEGY_SKIP
                    },
                ],
                pseudonymization_time=datetime(
                    2018, 3, 3, 12, 30, 0, tzinfo=timezone.utc
                ),
            ),
            new_pseudo=Pseudonymization(
                pseudonymization_time=datetime(
                    2025, 1, 1, 12, 30, 0, tzinfo=timezone.utc
                ),
            ),
            expected_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            expected_key=PAPIS_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {"keyId": PAPIS_ENCRYPTION_KEY_REFERENCE},
                {
                    PAPIS_ENCRYPTION_PARAMETER_STRATEGY: PAPIS_ENCRYPTION_PARAMETER_STRATEGY_SKIP
                },
            ],
            expected_pseudo_time=datetime(2025, 1, 1, 12, 30, 0, tzinfo=timezone.utc),
        ),
    ],
    ids=[
        "Add new pseudonymization PAPIS without stable ID - saved pseudonymization is None",
        "Add pseudonymization PAPIS without stable ID - no saved pseudonymization values",
        "No new pseudonymization - no default values set",
        "Add pseudonymization time PAPIS without stable ID",
        "Update pseudonymization time PAPIS without stable ID",
    ],
)
def test_add_default_pseudonymization_values_papis_without_stable_id(
    case: PseudoCase, metadata: Datadoc
):
    sykepenger = metadata.variables_lookup["sykepenger"]
    sykepenger.pseudonymization = case.existing_pseudo

    assert sykepenger.short_name is not None

    metadata.add_pseudonymization(sykepenger.short_name, case.new_pseudo)
    if sykepenger.pseudonymization:
        assert (
            sykepenger.pseudonymization.encryption_algorithm == case.expected_algorithm
        )
        assert sykepenger.pseudonymization.encryption_key_reference == case.expected_key
        assert (
            sykepenger.pseudonymization.pseudonymization_time
            == case.expected_pseudo_time
        )
        if sykepenger.pseudonymization.encryption_algorithm_parameters is None:
            assert case.expected_params is None
        else:
            _assert_dicts_in_list(
                case.expected_params,
                sykepenger.pseudonymization.encryption_algorithm_parameters,
            )


@pytest.mark.parametrize(
    "case",
    [
        PseudoCase(
            existing_pseudo=None,
            new_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
                stable_identifier_type=PAPIS_STABLE_IDENTIFIER_TYPE,
            ),
            expected_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            expected_stable_type=PAPIS_STABLE_IDENTIFIER_TYPE,
            expected_key=PAPIS_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {"keyId": PAPIS_ENCRYPTION_KEY_REFERENCE},
                {
                    PAPIS_WITH_STABLE_ID_ENCRYPTION_PARAMETER_SNAPSHOT_DATE: get_current_date()
                },
                {
                    PAPIS_ENCRYPTION_PARAMETER_STRATEGY: PAPIS_ENCRYPTION_PARAMETER_STRATEGY_SKIP
                },
            ],
            expected_pseudo_time=None,
        ),
        PseudoCase(
            existing_pseudo=Pseudonymization(),
            new_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
                stable_identifier_type=PAPIS_STABLE_IDENTIFIER_TYPE,
            ),
            expected_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            expected_stable_type=PAPIS_STABLE_IDENTIFIER_TYPE,
            expected_key=PAPIS_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {"keyId": PAPIS_ENCRYPTION_KEY_REFERENCE},
                {
                    PAPIS_WITH_STABLE_ID_ENCRYPTION_PARAMETER_SNAPSHOT_DATE: get_current_date()
                },
                {
                    PAPIS_ENCRYPTION_PARAMETER_STRATEGY: PAPIS_ENCRYPTION_PARAMETER_STRATEGY_SKIP
                },
            ],
            expected_pseudo_time=None,
        ),
        PseudoCase(
            existing_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            ),
            new_pseudo=None,
            expected_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            expected_stable_type=None,
            expected_key=None,
            expected_params=None,
            expected_pseudo_time=None,
        ),
        PseudoCase(
            existing_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
                encryption_key_reference=PAPIS_ENCRYPTION_KEY_REFERENCE,
                stable_identifier_type=PAPIS_STABLE_IDENTIFIER_TYPE,
                encryption_algorithm_parameters=[
                    {"keyId": PAPIS_ENCRYPTION_KEY_REFERENCE},
                    {
                        PAPIS_WITH_STABLE_ID_ENCRYPTION_PARAMETER_SNAPSHOT_DATE: get_current_date()
                    },
                    {
                        PAPIS_ENCRYPTION_PARAMETER_STRATEGY: PAPIS_ENCRYPTION_PARAMETER_STRATEGY_SKIP
                    },
                ],
            ),
            new_pseudo=Pseudonymization(
                pseudonymization_time=datetime(
                    2018, 3, 3, 12, 30, 0, tzinfo=timezone.utc
                ),
            ),
            expected_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            expected_stable_type=PAPIS_STABLE_IDENTIFIER_TYPE,
            expected_key=PAPIS_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {"keyId": PAPIS_ENCRYPTION_KEY_REFERENCE},
                {
                    PAPIS_ENCRYPTION_PARAMETER_STRATEGY: PAPIS_ENCRYPTION_PARAMETER_STRATEGY_SKIP
                },
            ],
            expected_pseudo_time=datetime(2018, 3, 3, 12, 30, 0, tzinfo=timezone.utc),
        ),
        PseudoCase(
            existing_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
                encryption_key_reference=PAPIS_ENCRYPTION_KEY_REFERENCE,
                stable_identifier_type=PAPIS_STABLE_IDENTIFIER_TYPE,
                encryption_algorithm_parameters=[
                    {"keyId": PAPIS_ENCRYPTION_KEY_REFERENCE},
                    {
                        PAPIS_WITH_STABLE_ID_ENCRYPTION_PARAMETER_SNAPSHOT_DATE: get_current_date()
                    },
                    {
                        PAPIS_ENCRYPTION_PARAMETER_STRATEGY: PAPIS_ENCRYPTION_PARAMETER_STRATEGY_SKIP
                    },
                ],
                pseudonymization_time=datetime(
                    2018, 3, 3, 12, 30, 0, tzinfo=timezone.utc
                ),
            ),
            new_pseudo=Pseudonymization(
                pseudonymization_time=datetime(
                    2025, 1, 1, 12, 30, 0, tzinfo=timezone.utc
                ),
            ),
            expected_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            expected_stable_type=PAPIS_STABLE_IDENTIFIER_TYPE,
            expected_key=PAPIS_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {"keyId": PAPIS_ENCRYPTION_KEY_REFERENCE},
                {
                    PAPIS_WITH_STABLE_ID_ENCRYPTION_PARAMETER_SNAPSHOT_DATE: get_current_date()
                },
                {
                    PAPIS_ENCRYPTION_PARAMETER_STRATEGY: PAPIS_ENCRYPTION_PARAMETER_STRATEGY_SKIP
                },
            ],
            expected_pseudo_time=datetime(2025, 1, 1, 12, 30, 0, tzinfo=timezone.utc),
        ),
        PseudoCase(
            existing_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
                encryption_key_reference=PAPIS_ENCRYPTION_KEY_REFERENCE,
                stable_identifier_type=PAPIS_STABLE_IDENTIFIER_TYPE,
                encryption_algorithm_parameters=[
                    {"keyId": PAPIS_ENCRYPTION_KEY_REFERENCE},
                    {
                        PAPIS_WITH_STABLE_ID_ENCRYPTION_PARAMETER_SNAPSHOT_DATE: get_current_date()
                    },
                    {
                        PAPIS_ENCRYPTION_PARAMETER_STRATEGY: PAPIS_ENCRYPTION_PARAMETER_STRATEGY_SKIP
                    },
                ],
            ),
            new_pseudo=Pseudonymization(
                stable_identifier_version="2023-01-01",
            ),
            expected_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            expected_stable_type=PAPIS_STABLE_IDENTIFIER_TYPE,
            expected_key=PAPIS_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {"keyId": PAPIS_ENCRYPTION_KEY_REFERENCE},
                {
                    PAPIS_ENCRYPTION_PARAMETER_STRATEGY: PAPIS_ENCRYPTION_PARAMETER_STRATEGY_SKIP
                },
            ],
            expected_stable_version="2023-01-01",
        ),
        PseudoCase(
            existing_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
                encryption_key_reference=PAPIS_ENCRYPTION_KEY_REFERENCE,
                stable_identifier_type=PAPIS_STABLE_IDENTIFIER_TYPE,
                stable_identifier_version="2023-01-01",
                encryption_algorithm_parameters=[
                    {"keyId": PAPIS_ENCRYPTION_KEY_REFERENCE},
                    {
                        PAPIS_WITH_STABLE_ID_ENCRYPTION_PARAMETER_SNAPSHOT_DATE: get_current_date()
                    },
                    {
                        PAPIS_ENCRYPTION_PARAMETER_STRATEGY: PAPIS_ENCRYPTION_PARAMETER_STRATEGY_SKIP
                    },
                ],
            ),
            new_pseudo=Pseudonymization(
                stable_identifier_version="2025-08-08",
            ),
            expected_algorithm=EncryptionAlgorithm.PAPIS_ENCRYPTION_ALGORITHM.value,
            expected_stable_type=PAPIS_STABLE_IDENTIFIER_TYPE,
            expected_key=PAPIS_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {"keyId": PAPIS_ENCRYPTION_KEY_REFERENCE},
                {
                    PAPIS_WITH_STABLE_ID_ENCRYPTION_PARAMETER_SNAPSHOT_DATE: get_current_date()
                },
                {
                    PAPIS_ENCRYPTION_PARAMETER_STRATEGY: PAPIS_ENCRYPTION_PARAMETER_STRATEGY_SKIP
                },
            ],
            expected_stable_version="2025-08-08",
        ),
    ],
    ids=[
        "Add new pseudonymization PAPIS with stable ID - saved pseudonymization is None",
        "Add pseudonymization PAPIS with stable ID - no saved pseudonymization values",
        "No new pseudonymization - no default values set",
        "Add pseudonymization time PAPIS with stable ID",
        "Update pseudonymization time PAPIS with stable ID",
        "Add stable version PAPIS with stable ID",
        "Update stable version PAPIS with stable ID",
    ],
)
def test_add_default_pseudonymization_values_papis_with_stable_id(
    case: PseudoCase, metadata: Datadoc
):
    sykepenger = metadata.variables_lookup["sykepenger"]
    sykepenger.pseudonymization = case.existing_pseudo

    assert sykepenger.short_name is not None

    metadata.add_pseudonymization(sykepenger.short_name, case.new_pseudo)
    if sykepenger.pseudonymization:
        assert (
            sykepenger.pseudonymization.stable_identifier_type
            == case.expected_stable_type
        )
        assert (
            sykepenger.pseudonymization.encryption_algorithm == case.expected_algorithm
        )
        assert sykepenger.pseudonymization.encryption_key_reference == case.expected_key
        assert (
            sykepenger.pseudonymization.stable_identifier_version
            == case.expected_stable_version
        )
        assert (
            sykepenger.pseudonymization.pseudonymization_time
            == case.expected_pseudo_time
        )
        algorithm_params = sykepenger.pseudonymization.encryption_algorithm_parameters
        if algorithm_params is None:
            assert case.expected_params is None
        else:
            _assert_dicts_in_list(
                case.expected_params,
                algorithm_params,
            )


@pytest.mark.parametrize(
    "case",
    [
        PseudoCase(
            existing_pseudo=None,
            new_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.DAED_ENCRYPTION_ALGORITHM.value,
            ),
            expected_algorithm=EncryptionAlgorithm.DAED_ENCRYPTION_ALGORITHM.value,
            expected_key=DAED_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {"keyId": DAED_ENCRYPTION_KEY_REFERENCE},
            ],
        ),
        PseudoCase(
            existing_pseudo=Pseudonymization(),
            new_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.DAED_ENCRYPTION_ALGORITHM.value,
            ),
            expected_algorithm=EncryptionAlgorithm.DAED_ENCRYPTION_ALGORITHM.value,
            expected_key=DAED_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {"keyId": DAED_ENCRYPTION_KEY_REFERENCE},
            ],
        ),
        PseudoCase(
            existing_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.DAED_ENCRYPTION_ALGORITHM.value,
            ),
            new_pseudo=None,
            expected_algorithm=EncryptionAlgorithm.DAED_ENCRYPTION_ALGORITHM.value,
        ),
        PseudoCase(
            existing_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.DAED_ENCRYPTION_ALGORITHM.value,
                encryption_key_reference=DAED_ENCRYPTION_KEY_REFERENCE,
                encryption_algorithm_parameters=[
                    {"keyId": DAED_ENCRYPTION_KEY_REFERENCE},
                ],
            ),
            new_pseudo=Pseudonymization(
                pseudonymization_time=datetime(
                    2018, 3, 3, 12, 30, 0, tzinfo=timezone.utc
                ),
            ),
            expected_algorithm=EncryptionAlgorithm.DAED_ENCRYPTION_ALGORITHM.value,
            expected_key=DAED_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {"keyId": DAED_ENCRYPTION_KEY_REFERENCE},
            ],
            expected_pseudo_time=datetime(2018, 3, 3, 12, 30, 0, tzinfo=timezone.utc),
        ),
        PseudoCase(
            existing_pseudo=Pseudonymization(
                encryption_algorithm=EncryptionAlgorithm.DAED_ENCRYPTION_ALGORITHM.value,
                encryption_key_reference=DAED_ENCRYPTION_KEY_REFERENCE,
                encryption_algorithm_parameters=[
                    {"keyId": DAED_ENCRYPTION_KEY_REFERENCE},
                ],
                pseudonymization_time=datetime(
                    2018, 3, 3, 12, 30, 0, tzinfo=timezone.utc
                ),
            ),
            new_pseudo=Pseudonymization(
                pseudonymization_time=datetime(
                    2025, 1, 1, 12, 30, 0, tzinfo=timezone.utc
                ),
            ),
            expected_algorithm=EncryptionAlgorithm.DAED_ENCRYPTION_ALGORITHM.value,
            expected_key=DAED_ENCRYPTION_KEY_REFERENCE,
            expected_params=[
                {"keyId": DAED_ENCRYPTION_KEY_REFERENCE},
            ],
            expected_pseudo_time=datetime(2025, 1, 1, 12, 30, 0, tzinfo=timezone.utc),
        ),
    ],
    ids=[
        "Add new pseudonymization DAED - saved pseudonymization is None",
        "Add pseudonymization DAED - no saved pseudonymization values",
        "No new pseudonymization - no default values set",
        "Add pseudonymization time DAED",
        "Update pseudonymization time DAED",
    ],
)
def test_add_default_pseudonymization_values_daed(case: PseudoCase, metadata: Datadoc):
    sykepenger = metadata.variables_lookup["sykepenger"]
    sykepenger.pseudonymization = case.existing_pseudo

    assert sykepenger.short_name is not None
    metadata.add_pseudonymization(sykepenger.short_name, case.new_pseudo)
    if sykepenger.pseudonymization:
        assert (
            sykepenger.pseudonymization.encryption_algorithm == case.expected_algorithm
        )
        assert sykepenger.pseudonymization.encryption_key_reference == case.expected_key
        assert (
            sykepenger.pseudonymization.stable_identifier_version
            == case.expected_stable_version
        )
        algorithm_params = sykepenger.pseudonymization.encryption_algorithm_parameters
        if algorithm_params is None:
            assert case.expected_params is None
        else:
            _assert_dicts_in_list(
                case.expected_params,
                algorithm_params,
            )


@pytest.mark.parametrize(
    "case",
    [
        PseudoCase(
            existing_pseudo=None,
            new_pseudo=Pseudonymization(
                encryption_algorithm="unknown",
            ),
            expected_algorithm="unknown",
        ),
    ],
    ids=[
        "Add new unknown - saved pseudonymization is None",
    ],
)
def test_add_pseudonymization_unknown_algorithm(case: PseudoCase, metadata: Datadoc):
    sykepenger = metadata.variables_lookup["sykepenger"]
    sykepenger.pseudonymization = case.existing_pseudo

    assert sykepenger.short_name is not None

    metadata.add_pseudonymization(sykepenger.short_name, case.new_pseudo)
    if sykepenger.pseudonymization:
        assert (
            sykepenger.pseudonymization.encryption_algorithm == case.expected_algorithm
        )
        assert sykepenger.pseudonymization.encryption_key_reference == case.expected_key
        assert (
            sykepenger.pseudonymization.stable_identifier_version
            == case.expected_stable_version
        )
        algorithm_params = sykepenger.pseudonymization.encryption_algorithm_parameters
        if algorithm_params is None:
            assert case.expected_params is None
        else:
            _assert_dicts_in_list(
                case.expected_params,
                algorithm_params,
            )


@pytest.mark.parametrize(
    "existing_metadata_path",
    [TEST_PSEUDO_DIRECTORY / "dataset_and_pseudo"],
)
def test_add_pseudo_variable(
    existing_metadata_file: Path,  # noqa: ARG001
    metadata: Datadoc,
):
    test_variable = "sykepenger"
    is_personal_data = metadata.variables_lookup[test_variable].is_personal_data
    metadata.add_pseudonymization(test_variable)
    assert metadata.variables_lookup[test_variable].pseudonymization is not None
    assert metadata.variables_lookup[test_variable].is_personal_data == is_personal_data


@pytest.mark.parametrize(
    "existing_metadata_path",
    [TEST_PSEUDO_DIRECTORY / "dataset_and_pseudo"],
)
def test_add_pseudo_variable_non_existent_variable_name(
    existing_metadata_file: Path,  # noqa: ARG001
    metadata: Datadoc,
):
    with pytest.raises(KeyError):
        metadata.add_pseudonymization("new_pseudo_variable")


@pytest.mark.parametrize(
    "existing_metadata_path",
    [TEST_PSEUDO_DIRECTORY / "dataset_and_pseudo"],
)
def test_existing_metadata_file_update_pseudonymization(
    existing_metadata_file: Path,  # noqa: ARG001
    metadata: Datadoc,
):
    metadata.add_pseudonymization("pers_id")
    variable = metadata.variables_lookup["pers_id"]

    assert variable.pseudonymization is not None
    assert variable.pseudonymization.encryption_algorithm is None
    variable.pseudonymization.encryption_algorithm = "new_encryption_algorithm"
    assert variable.pseudonymization.encryption_algorithm == "new_encryption_algorithm"


@pytest.mark.parametrize(
    "existing_metadata_path",
    [TEST_PSEUDO_DIRECTORY / "dataset_and_pseudo"],
)
def test_update_pseudo(
    existing_metadata_file: Path,  # noqa: ARG001
    metadata: Datadoc,
):
    variable = metadata.variables_lookup["pers_id"]

    pseudo = Pseudonymization(encryption_algorithm="new_encryption_algorithm")

    metadata.add_pseudonymization("pers_id", pseudo)

    assert variable.pseudonymization is not None
    assert variable.pseudonymization.encryption_algorithm == "new_encryption_algorithm"
    assert variable.pseudonymization.encryption_algorithm_parameters is None


@pytest.mark.parametrize(
    "existing_metadata_path",
    [TEST_PSEUDO_DIRECTORY / "dataset_and_pseudo"],
)
def test_remove_pseudo_variable(
    existing_metadata_file: Path,  # noqa: ARG001
    metadata: Datadoc,
):
    test_variable = "alm_inntekt"
    is_personal_data = metadata.variables_lookup[test_variable].is_personal_data
    metadata.remove_pseudonymization(test_variable)
    assert metadata.variables_lookup[test_variable].is_personal_data == is_personal_data
    assert metadata.variables_lookup[test_variable].pseudonymization is None


@pytest.mark.parametrize(
    "existing_metadata_path",
    [TEST_PSEUDO_DIRECTORY / "dataset_and_pseudo"],
)
def test_remove_pseudo_variable_non_existent_variable_name(
    existing_metadata_file: Path,  # noqa: ARG001
    metadata: Datadoc,
):
    with pytest.raises(KeyError):
        metadata.remove_pseudonymization("fnr")
