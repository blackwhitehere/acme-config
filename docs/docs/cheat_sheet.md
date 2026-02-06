# Cheat Sheet

## Declare config schema

```python
from acme_config import AppConfig, ConfigField


class MyConfig(AppConfig):
    model_config = {"env_prefix": "MYAPP_"}

    bucket: str = ConfigField(description="S3 bucket", cli_flag="--bucket")
    debug: bool = ConfigField(default=False, description="Debug mode")
```

## Resolve config (defaults < .env < env vars < CLI < overrides)

```python
from acme_config import build_cli_parser, resolve_config


parser = build_cli_parser(MyConfig)
cli_args = vars(parser.parse_args())
config = resolve_config(MyConfig, cli_args=cli_args)
```

## Feature flags

```python
from acme_config import FeatureFlag, FeatureFlags


class MyFeatures(FeatureFlags):
    model_config = {"env_prefix": "MYAPP_FEATURE_"}

    new_ui: bool = FeatureFlag(default=False, description="Enable new UI")
```

## Generate templates and manifests

```python
from acme_config import generate_dotenv_template, generate_manifest

print(generate_dotenv_template(MyConfig))
print(generate_manifest(MyConfig))
```