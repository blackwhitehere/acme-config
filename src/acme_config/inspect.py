"""Config inspection utilities.

Generate manifests, dotenv templates, validate environments, and
describe config instances with secret redaction.
"""

from __future__ import annotations

from typing import Any

from acme_config.resolver import _get_field_metadata
from acme_config.schema import AppConfig


def generate_manifest(config_class: type[AppConfig]) -> str:
    """Generate an env.manifest from a config class.

    Produces a machine-readable manifest listing all env vars the app expects.
    """
    lines = [
        "# Environment variable manifest",
        f"# Generated from {config_class.__name__}",
        "#",
        "# Format: ENV_VAR_NAME  # description [required|default=value]",
        "",
    ]

    prefix = config_class.model_config.get("env_prefix", "")
    metadata = _get_field_metadata(config_class)

    for field_name, meta in metadata.items():
        env_var = f"{prefix}{field_name}".upper()
        desc = meta["description"]
        if meta["required"]:
            suffix = "# required"
        elif meta["default"] is not None:
            suffix = f"# default={meta['default']}"
        else:
            suffix = "# optional"
        if meta["secret"]:
            suffix += " [secret]"

        line = f"{env_var}  {suffix}"
        if desc:
            line = f"{env_var}  # {desc} [{suffix.lstrip('# ')}]"
        lines.append(line)

    return "\n".join(lines) + "\n"


def generate_dotenv_template(config_class: type[AppConfig]) -> str:
    """Generate a .env.example template from a config class."""
    lines = [
        f"# .env template for {config_class.__name__}",
        "# Copy to .env and fill in values",
        "",
    ]

    prefix = config_class.model_config.get("env_prefix", "")
    metadata = _get_field_metadata(config_class)

    for field_name, meta in metadata.items():
        env_var = f"{prefix}{field_name}".upper()
        desc = meta["description"]
        if desc:
            lines.append(f"# {desc}")

        if meta["required"]:
            lines.append(f"{env_var}=")
        elif meta["default"] is not None:
            lines.append(f"# {env_var}={meta['default']}")
        else:
            lines.append(f"# {env_var}=")
        lines.append("")

    return "\n".join(lines)


def validate_env(config_class: type[AppConfig]) -> list[str]:
    """Check the current environment for missing required config.

    Returns a list of issue descriptions. Empty list means all is well.
    """
    issues: list[str] = []

    try:
        config_class()
    except Exception as e:
        # Parse pydantic validation errors
        error_str = str(e)
        for line in error_str.splitlines():
            line = line.strip()
            if line and not line.startswith("For further"):
                issues.append(line)

    return issues


def describe_config(config: AppConfig) -> str:
    """Pretty-print a config instance with secret fields redacted.

    Useful for startup logging to confirm which config values are active.
    """
    lines: list[str] = [f"{config.__class__.__name__}:"]
    metadata = _get_field_metadata(config.__class__)

    for field_name, meta in metadata.items():
        value: Any = getattr(config, field_name)
        if meta["secret"]:
            display = "***"
        else:
            display = repr(value)
        lines.append(f"  {field_name} = {display}")

    return "\n".join(lines)
