import pytest

from dapla_metadata._shared.config import DAPLA_ENVIRONMENT
from dapla_metadata._shared.config import DAPLA_GROUP_CONTEXT
from dapla_metadata._shared.config import OIDC_TOKEN
from dapla_metadata._shared.enums import DaplaEnvironment
from dapla_metadata.variable_definitions.config import VARDEF_HOST_TEST
from dapla_metadata.variable_definitions.config import get_active_group
from dapla_metadata.variable_definitions.config import get_vardef_client_configuration
from dapla_metadata.variable_definitions.config import get_vardef_host


@pytest.mark.parametrize(
    "env",
    [DaplaEnvironment.PROD.value, DaplaEnvironment.DEV.value],
)
def test_vardef_host_unavailable(monkeypatch: pytest.MonkeyPatch, env: str):
    monkeypatch.setenv(DAPLA_ENVIRONMENT, env)
    with pytest.raises(NotImplementedError):
        get_vardef_host()


def test_vardef_host_test(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(DAPLA_ENVIRONMENT, DaplaEnvironment.TEST.value)
    assert get_vardef_host() == VARDEF_HOST_TEST


def test_vardef_host_default(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv(DAPLA_ENVIRONMENT, raising=False)
    monkeypatch.delenv("VARDEF_HOST", raising=False)
    assert get_vardef_host() == "http://localhost:8080"


def test_vardef_host_specified(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv(DAPLA_ENVIRONMENT, raising=False)
    monkeypatch.setenv("VARDEF_HOST", "my-host")
    assert get_vardef_host() == "my-host"


def test_get_vardef_client_configuration(
    monkeypatch: pytest.MonkeyPatch,
    fake_jwt: str,
):
    monkeypatch.setenv(DAPLA_ENVIRONMENT, DaplaEnvironment.TEST.value)
    monkeypatch.setenv(OIDC_TOKEN, fake_jwt)
    config = get_vardef_client_configuration()
    assert config.host is not None
    assert config.access_token is not None


def test_active_group_unset(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv(DAPLA_GROUP_CONTEXT, raising=False)
    with pytest.raises(
        OSError,
        match="Environment variable DAPLA_GROUP_CONTEXT not defined",
    ):
        get_active_group()


def test_active_group_set(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(DAPLA_GROUP_CONTEXT, "my-group")
    assert get_active_group() == "my-group"