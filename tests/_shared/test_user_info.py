import pytest

from dapla_metadata._shared import user_info
from dapla_metadata._shared.enums import DaplaRegion
from dapla_metadata._shared.enums import DaplaService
from dapla_metadata._shared.user_info import PLACEHOLDER_EMAIL_ADDRESS
from dapla_metadata._shared.user_info import DaplaLabUserInfo
from dapla_metadata._shared.user_info import JupyterHubUserInfo
from dapla_metadata._shared.user_info import UnknownUserInfo
from dapla_metadata._shared.user_info import UserInfo
from tests.utils.constants import DAPLA_GROUP_CONTEXT
from tests.utils.constants import DAPLA_REGION
from tests.utils.constants import DAPLA_SERVICE
from tests.utils.constants import JUPYTERHUB_USER


@pytest.mark.parametrize(
    ("environment_variable_name", "environment_variable_value", "expected_class"),
    [
        (DAPLA_SERVICE, DaplaService.JUPYTERLAB.value, JupyterHubUserInfo),
        (DAPLA_REGION, DaplaRegion.DAPLA_LAB.value, DaplaLabUserInfo),
        (None, None, UnknownUserInfo),
    ],
)
def test_get_user_info_for_current_platform(
    monkeypatch: pytest.MonkeyPatch,
    environment_variable_name: str,
    environment_variable_value: str,
    expected_class: type[UserInfo],
):
    if environment_variable_name:
        monkeypatch.setenv(environment_variable_name, environment_variable_value)
    assert isinstance(user_info.get_user_info_for_current_platform(), expected_class)


def test_jupyterhub_user_info_short_email(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(JUPYTERHUB_USER, PLACEHOLDER_EMAIL_ADDRESS)
    assert JupyterHubUserInfo().short_email == PLACEHOLDER_EMAIL_ADDRESS


def test_dapla_lab_user_info_short_email(
    fake_jwt: str,
    raw_jwt_payload: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("OIDC_TOKEN", fake_jwt)
    assert DaplaLabUserInfo().short_email == raw_jwt_payload["email"]


def test_dapla_lab_user_info_short_email_no_jwt_available():
    assert DaplaLabUserInfo().short_email is None


@pytest.mark.parametrize(("raw_jwt_payload"), [{"no_email": "no_email_in_jwt"}])
def test_dapla_lab_user_info_short_email_no_email_in_jwt(
    fake_jwt: str,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("OIDC_TOKEN", fake_jwt)
    assert DaplaLabUserInfo().short_email is None


@pytest.mark.parametrize(
    ("environment_variable_name", "environment_variable_value", "expected_team"),
    [
        (DAPLA_GROUP_CONTEXT, "dapla-metadata-developers", "dapla-metadata"),
        (
            DAPLA_GROUP_CONTEXT,
            "dapla-metadata-data-admins",
            "dapla-metadata",
        ),
        (DAPLA_GROUP_CONTEXT, "dapla-metadata-dev", "dapla-metadata"),
        (DAPLA_GROUP_CONTEXT, "dapla-metadata", "dapla"),
        (
            DAPLA_GROUP_CONTEXT,
            "dapla-metadata-not-a-real-group",
            "dapla-metadata-not-a-real",
        ),
    ],
)
def test_get_owner(
    monkeypatch: pytest.MonkeyPatch,
    environment_variable_name: str,
    environment_variable_value: str,
    expected_team: str,
):
    if environment_variable_name:
        monkeypatch.setenv(environment_variable_name, environment_variable_value)
    assert user_info.get_owner() == expected_team


@pytest.mark.parametrize(
    ("environment_variable_name", "environment_variable_value"),
    [
        (None, None),
        (DAPLA_GROUP_CONTEXT, ""),
    ],
)
def test_get_owner_errors(
    monkeypatch: pytest.MonkeyPatch,
    environment_variable_name: str,
    environment_variable_value: str,
):
    if environment_variable_name:
        monkeypatch.setenv(environment_variable_name, environment_variable_value)

    with pytest.raises(
        OSError,
        match="DAPLA_GROUP_CONTEXT environment variable not found",
    ) as exc_info:  # Step 1: Expect an exception
        user_info.get_owner()

    assert str(exc_info.value) == "DAPLA_GROUP_CONTEXT environment variable not found"