"""App configuration framework: schema declaration, env/CLI resolution, feature flags."""

from acme_config.features import FeatureFlag, FeatureFlags, list_flags
from acme_config.inspect import (
    describe_config,
    generate_dotenv_template,
    generate_manifest,
    validate_env,
)
from acme_config.resolver import build_cli_parser, resolve_config
from acme_config.schema import AppConfig, ConfigField

__all__ = [
    # Schema
    "AppConfig",
    "ConfigField",
    # Feature flags
    "FeatureFlags",
    "FeatureFlag",
    "list_flags",
    # Resolver
    "resolve_config",
    "build_cli_parser",
    # Inspection
    "validate_env",
    "describe_config",
    "generate_manifest",
    "generate_dotenv_template",
]
