"""Feature flag support.

Apps subclass `FeatureFlags` to declare boolean features that can be
toggled via environment variables.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings


def FeatureFlag(
    default: bool = False,
    *,
    description: str = "",
    **kwargs: Any,
) -> Any:
    """Declare a feature flag.

    Args:
        default: Whether the feature is enabled by default.
        description: Human-readable description of the feature.
    """
    return Field(default=default, description=description, **kwargs)


class FeatureFlags(BaseSettings):
    """Base class for feature flag declarations.

    Subclass this and declare boolean fields for each feature.
    Values are loaded from environment variables using the configured prefix.

    Example::

        class MyFeatures(FeatureFlags):
            model_config = {"env_prefix": "MYAPP_FEATURE_"}

            new_dashboard: bool = FeatureFlag(
                default=False, description="Enable new dashboard UI"
            )
            parallel_processing: bool = FeatureFlag(
                default=True, description="Use parallel data processing"
            )

    Required: set `model_config = {"env_prefix": "APP_FEATURE_"}` in your subclass.
    """

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    def is_enabled(self, flag_name: str) -> bool:
        """Check if a feature flag is enabled by name.

        Args:
            flag_name: The field name of the flag.

        Raises:
            AttributeError: If the flag doesn't exist.
        """
        value = getattr(self, flag_name)
        if not isinstance(value, bool):
            raise TypeError(f"Flag '{flag_name}' is not a boolean field")
        return value


def list_flags(features: FeatureFlags) -> list[dict[str, Any]]:
    """List all feature flags with their current state.

    Returns a list of dicts with keys: name, value, description, default.
    Useful for admin/debug endpoints.
    """
    result: list[dict[str, Any]] = []
    for name, field_info in features.__class__.model_fields.items():
        value = getattr(features, name)
        if not isinstance(value, bool):
            continue
        result.append({
            "name": name,
            "value": value,
            "description": field_info.description or "",
            "default": field_info.default,
        })
    return result
