from enum import StrEnum


class DaplaRegion(StrEnum):
    """Dapla platforms/regions."""

    DAPLA_LAB = "DAPLA_LAB"
    ON_PREM = "ON_PREM"
    CLOUD_RUN = "CLOUD_RUN"


class DaplaEnvironment(StrEnum):
    """Dapla lifecycle environment."""

    PROD = "PROD"
    TEST = "TEST"
    DEV = "DEV"


class DaplaService(StrEnum):
    """Dapla services."""

    DATADOC = "DATADOC"
    JUPYTERLAB = "JUPYTERLAB"
    VS_CODE = "VS_CODE"
    R_STUDIO = "R_STUDIO"
    KILDOMATEN = "KILDOMATEN"
