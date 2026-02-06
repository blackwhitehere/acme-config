# Description

App configuration framework: schema declaration, env/CLI resolution, feature flags.

## Motivation

Applications need a consistent way to declare config, load values from `.env` and
environment variables, and override settings from CLI arguments. acme-config provides
that with a typed schema, a resolver with clear precedence, and inspection helpers.

## Features

* Declare config schemas with `AppConfig` and `ConfigField`.
* Resolve settings from defaults, `.env`, environment variables, CLI args, and overrides.
* Generate argparse parsers from config schema metadata.
* Inspect configuration: manifest generation, dotenv templates, validation, redaction.
* Feature flags via `FeatureFlags` and `FeatureFlag`.

## Example usage

```python
from acme_config import AppConfig, ConfigField, build_cli_parser, resolve_config


class MyConfig(AppConfig):
    model_config = {"env_prefix": "MYAPP_"}

    bucket: str = ConfigField(description="S3 bucket", cli_flag="--bucket")
    debug: bool = ConfigField(default=False, description="Debug mode", cli_flag="--debug")


parser = build_cli_parser(MyConfig)
cli_args = vars(parser.parse_args())
config = resolve_config(MyConfig, cli_args=cli_args)
```

## Legacy AWS Parameter Store CLI

The AWS Parameter Store CLI (`ac` command) from acme-config v0.0.x lives in
`src/acme_config/legacy`. It is not part of the v0.1.0 API and is slated to
move into acme-env or acme-runtime.