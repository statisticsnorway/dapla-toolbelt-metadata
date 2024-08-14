"""Configuration management for dataset package."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from pprint import pformat

from dotenv import dotenv_values
from dotenv import load_dotenv

from dataset.utility.enums import DaplaRegion
from dataset.utility.enums import DaplaService

logging.basicConfig(level=logging.DEBUG, force=True)

logger = logging.getLogger(__name__)

DOT_ENV_FILE_PATH = Path(__file__).parent.joinpath(".env")

JUPYTERHUB_USER = "JUPYTERHUB_USER"
DAPLA_REGION = "DAPLA_REGION"
DAPLA_SERVICE = "DAPLA_SERVICE"

env_loaded = False


def _load_dotenv_file() -> None:
    global env_loaded  # noqa: PLW0603
    if not env_loaded and DOT_ENV_FILE_PATH.exists():
        load_dotenv(DOT_ENV_FILE_PATH)
        env_loaded = True
        logger.info(
            "Loaded .env file with config keys: \n%s",
            pformat(list(dotenv_values(DOT_ENV_FILE_PATH).keys())),
        )


def _get_config_item(item: str) -> str | None:
    """Get a config item. Makes sure all access is logged."""
    _load_dotenv_file()
    value = os.getenv(item)
    logger.debug("Config accessed. %s", item)
    return value


def get_jupyterhub_user() -> str | None:
    """Get the JupyterHub user name."""
    return _get_config_item(JUPYTERHUB_USER)


def get_statistical_subject_source_url() -> str | None:
    """Get the URL to the statistical subject source."""
    return _get_config_item("DATADOC_STATISTICAL_SUBJECT_SOURCE_URL")


def get_dapla_region() -> DaplaRegion | None:
    """Get the Dapla region we're running on."""
    if region := _get_config_item(DAPLA_REGION):
        return DaplaRegion(region)

    return None


def get_dapla_service() -> DaplaService | None:
    """Get the Dapla service we're running on."""
    if service := _get_config_item(DAPLA_SERVICE):
        return DaplaService(service)

    return None


def get_oidc_token() -> str | None:
    """Get the JWT token from the environment."""
    return _get_config_item("OIDC_TOKEN")
