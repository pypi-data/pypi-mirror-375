"""
Configure prima environment settings.

Settings are satisfied from os.environ, or the .env file, finally falling back to default
declared in PrimaSettings below. This allows for easy configuration for local execution
or docker deployment.
"""

import importlib.metadata

from pydantic_settings import BaseSettings, SettingsConfigDict


def _package_version(distribution_name: str | None) -> str:
    """Return the version from the given distribution or fault if not set."""
    if not distribution_name:
        msg = "PRIMA_PACKAGE_NAME must be set in .env or os.environ"
        raise KeyError(msg)
    return importlib.metadata.version(distribution_name)


class PrimaSettings(BaseSettings):
    """Application settings for prima service."""

    model_config = SettingsConfigDict(env_file=".env", extra="allow", env_ignore_empty=True)

    prima_package_name: str | None = None

    @property
    def package_version(self) -> str:
        return _package_version(self.prima_package_name)

    logfire_token: str | None = None
    otel_exporter_otlp_endpoint: str | None = None
