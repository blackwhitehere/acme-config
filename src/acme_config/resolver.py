"""Config resolution: merge .env, environment, CLI args, and overrides."""

from __future__ import annotations

import argparse
from typing import Any

from acme_config.schema import AppConfig


def _get_field_metadata(config_class: type[AppConfig]) -> dict[str, dict[str, Any]]:
    """Extract field metadata (cli_flag, secret, description) from config class."""
    result: dict[str, dict[str, Any]] = {}
    for name, field_info in config_class.model_fields.items():
        extra = field_info.json_schema_extra or {}
        result[name] = {
            "cli_flag": extra.get("cli_flag"),
            "secret": extra.get("secret", False),
            "description": field_info.description or "",
            "default": field_info.default,
            "required": field_info.is_required(),
            "annotation": field_info.annotation,
        }
    return result


def build_cli_parser(
    config_class: type[AppConfig],
    prog: str | None = None,
    description: str | None = None,
) -> argparse.ArgumentParser:
    """Generate an argparse parser from a config class.

    Only fields with `cli_flag` set will become CLI arguments.

    Args:
        config_class: The AppConfig subclass to generate a parser for.
        prog: Program name for the parser.
        description: Description for the parser.
    """
    parser = argparse.ArgumentParser(prog=prog, description=description)
    metadata = _get_field_metadata(config_class)

    for field_name, meta in metadata.items():
        cli_flag = meta["cli_flag"]
        if not cli_flag:
            continue

        kwargs: dict[str, Any] = {}
        kwargs["dest"] = field_name
        kwargs["help"] = meta["description"]

        annotation = meta["annotation"]
        if annotation is bool:
            # Boolean fields become --flag / --no-flag
            if meta["default"] is False:
                kwargs["action"] = "store_true"
            else:
                kwargs["action"] = "store_false"
        else:
            kwargs["type"] = str  # Let pydantic handle type coercion
            if not meta["required"] and meta["default"] is not None:
                kwargs["default"] = None  # None = "not provided via CLI"

        parser.add_argument(cli_flag, **kwargs)

    return parser


def resolve_config[T: AppConfig](
    config_class: type[T],
    cli_args: dict[str, Any] | None = None,
    overrides: dict[str, Any] | None = None,
    env_file: str | None = None,
) -> T:
    """Create a config instance with full precedence resolution.

    Resolution order (later overrides earlier):
    1. Field defaults
    2. .env file
    3. Environment variables
    4. CLI args (if provided)
    5. Explicit overrides (if provided)

    Args:
        config_class: The AppConfig subclass to instantiate.
        cli_args: Dict of CLI argument values (e.g. from argparse).
            Keys with None values are skipped (not provided).
        overrides: Dict of explicit override values (highest priority).
        env_file: Path to .env file. If None, uses the class default.
    """
    # Build kwargs for pydantic-settings constructor
    init_kwargs: dict[str, Any] = {}

    # env_file override
    if env_file is not None:
        init_kwargs["_env_file"] = env_file

    # CLI args — only include non-None values (None = not provided via CLI)
    if cli_args:
        for key, value in cli_args.items():
            if value is not None:
                init_kwargs[key] = value

    # Explicit overrides — highest priority
    if overrides:
        init_kwargs.update(overrides)

    return config_class(**init_kwargs)
