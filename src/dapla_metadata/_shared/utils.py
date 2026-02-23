from importlib import metadata

DAPLA_TOOLBELT_METADATA_PACKAGE_NAME = "dapla-toolbelt-metadata"
TEAM_METADATA_CONTACT_EMAIL = "metadata@ssb.no"


def get_app_version() -> str:
    """Get the version of the this package."""
    return metadata.distribution(DAPLA_TOOLBELT_METADATA_PACKAGE_NAME).version


def get_user_agent() -> str:
    """Get the value for the Use-Agent header."""
    return f"{DAPLA_TOOLBELT_METADATA_PACKAGE_NAME}/{get_app_version()} ({TEAM_METADATA_CONTACT_EMAIL})"
