"""App configuration schema declaration.

Apps subclass `AppConfig` to declare what configuration they need.
Fields are loaded from .env files and environment variables automatically
via pydantic-settings, with optional CLI flag mapping.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings


def ConfigField(
    default: Any = ...,
    *,
    description: str = "",
    cli_flag: str | None = None,
    secret: bool = False,
    **kwargs: Any,
) -> Any:
    """Declare a configuration field with metadata.

    Args:
        default: Default value. Use `...` (Ellipsis) for required fields.
        description: Human-readable description of this config option.
        cli_flag: CLI argument name (e.g. "--bucket-name"). If set,
            `build_cli_parser()` will generate this argument automatically.
        secret: If True, value is redacted in `describe_config()` output.
        **kwargs: Additional arguments passed to pydantic `Field`.
    """
    json_schema_extra = {
        "cli_flag": cli_flag,
        "secret": secret,
    }
    return Field(
        default=default,
        description=description,
        json_schema_extra=json_schema_extra,
        **kwargs,
    )


class AppConfig(BaseSettings):
    """Base class for app configuration.

    Subclass this and declare fields to define what configuration your
    app needs. Values are resolved from (in order of precedence):
    defaults < .env file < environment variables < CLI args < explicit overrides.

    Example::

        class MyConfig(AppConfig):
            model_config = {"env_prefix": "MYAPP_"}

            bucket_name: str = ConfigField(description="S3 bucket", cli_flag="--bucket")
            debug: bool = ConfigField(default=False, description="Debug mode")
            db_password: str = ConfigField(description="DB password", secret=True)

    Required: set `model_config = {"env_prefix": "PREFIX_"}` in your subclass.
    """

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}
