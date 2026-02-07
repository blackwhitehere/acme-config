# acme-config

## Description

Standard for providing configuration to applications.

## Context

There are repeatable patterns that need to be implemented when building configuration into an app:
* Loading values from underlying storage
* Combining values from baked-in defaults, CLI arguments and provided config
* Ensuring provided configuration is well specified
* Viewing & inspecting app configuration
* Manage common config features like feature flags

## Features

* Declare config validation schemas with `AppConfig` and `ConfigField`.
* Resolve settings from defaults, `.env` file, environment variables, CLI args.
* Generate argparse parsers from config schema metadata with built in resolution order logic.
* Inspect configuration: manifest generation, dotenv templates, validation.
* Access feature flags via `FeatureFlags` and `FeatureFlag`.

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

### Why `build_cli_parser` and `resolve_config` are separate

`build_cli_parser` generates an argparse parser from your schema — it only handles CLI argument
parsing. `resolve_config` handles **precedence merging**: filtering out unset CLI args, layering
in overrides, and constructing the final config instance. Not all apps use CLI arguments — some
resolve config entirely from env vars, `.env` files, or explicit overrides:

```python
# Without CLI — resolve from env vars and overrides only
config = resolve_config(MyConfig, overrides={"debug": True})

# With a custom .env file
config = resolve_config(MyConfig, env_file="production.env")

# Full flow with CLI args
config = resolve_config(MyConfig, cli_args=vars(parser.parse_args()))
```

Resolution order (later overrides earlier):
1. Field defaults
2. `.env` file
3. Environment variables
4. CLI args
5. Explicit overrides

### About `model_config`

Subclasses must set `model_config = {"env_prefix": "PREFIX_"}` to control which
environment variables map to their fields. Without it, field names map to bare env
var names (e.g. `NAME` instead of `MYAPP_NAME`), causing collisions between apps.
The `AppConfig` base class provides defaults for `.env` file loading and unknown-field
handling. Pydantic v2 merges child config with parent, so the subclass only needs to
add `env_prefix`:

```python
class MyConfig(AppConfig):
    # Inherits env_file=".env", env_file_encoding="utf-8", extra="ignore" from AppConfig.
    # Only env_prefix is needed here.
    model_config = {"env_prefix": "MYAPP_"}

    bucket: str = ConfigField(description="S3 bucket")
```

Fields are then loaded from env vars like `MYAPP_BUCKET`.

## Config Inspection

The inspection module generates artifacts from your config schema for ops and developer use.

### Manifest Generation

`generate_manifest` produces a machine-readable listing of all env vars an app expects,
marking each as required, optional, or secret:

```python
from acme_config import generate_manifest

manifest = generate_manifest(MyConfig)
print(manifest)
# Output:
# MYAPP_BUCKET  # S3 bucket [required]
# MYAPP_DEBUG  # Debug mode [default=False]
```

### Dotenv Templates

`generate_dotenv_template` creates a `.env.example` file from your schema. Required
fields get empty values; fields with defaults are commented out:

```python
from acme_config import generate_dotenv_template

template = generate_dotenv_template(MyConfig)
print(template)
# Output:
# # S3 bucket
# MYAPP_BUCKET=
#
# # Debug mode
# # MYAPP_DEBUG=False
```

### Validation

`validate_env` checks the current environment against the schema and returns a list
of issues (missing required fields, type errors). An empty list means all is well:

```python
from acme_config import validate_env

issues = validate_env(MyConfig)
if issues:
    for issue in issues:
        print(f"Config problem: {issue}")
```

### Describe Config

`describe_config` pretty-prints a config instance with secret fields redacted. Useful
for startup logging:

```python
from acme_config import describe_config

config = resolve_config(MyConfig)
print(describe_config(config))
# MyConfig:
#   bucket = 'my-data-bucket'
#   debug = False
#   db_password = ***
```

## Feature Flags

`FeatureFlags` and `FeatureFlag` provide boolean feature toggles loaded from
environment variables. Subclass `FeatureFlags`, declare boolean fields with
`FeatureFlag`, and set `model_config` with an `env_prefix`:

```python
from acme_config import FeatureFlags, FeatureFlag, list_flags


class MyFeatures(FeatureFlags):
    model_config = {"env_prefix": "MYAPP_FEATURE_"}

    new_dashboard: bool = FeatureFlag(default=False, description="Enable new dashboard UI")
    parallel: bool = FeatureFlag(default=True, description="Use parallel processing")


# Load from environment (e.g. MYAPP_FEATURE_NEW_DASHBOARD=true)
features = MyFeatures()

# Check flags
features.is_enabled("new_dashboard")  # False (default)
features.parallel                     # True (default)

# List all flags for admin/debug endpoints
for flag in list_flags(features):
    print(f"{flag['name']}: {flag['value']} (default={flag['default']})")
```

## Legacy AWS Parameter Store CLI

The AWS Parameter Store CLI (`ac` command) from acme-config v0.0.x lives in
`src/acme_config/legacy`. It is not part of the v0.1.0 API and is slated to
move into acme-env or acme-runtime.

# Dev environment

The project comes with a python development environment.
To generate it, after checking out the repo run:

    chmod +x create_env.sh

Then to generate the environment (or update it to latest version based on state of `uv.lock`), run:

    ./create_env.sh

This will generate a new python virtual env under `.venv` directory. You can activate it via:

    source .venv/bin/activate

If you are using VSCode, set to use this env via `Python: Select Interpreter` command.

# Project template

This project has been setup with `acme-project-create`, a python code template library.

# Required setup post use

* Enable GitHub Pages to be published via [GitHub Actions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site#publishing-with-a-custom-github-actions-workflow) by going to `Settings-->Pages-->Source`
* Create `release` environment for [GitHub Actions](https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-deployments/managing-environments-for-deployment#creating-an-environment) to enable uploads of the library to PyPi
* Setup auth to PyPI for the GitHub Action implemented in `.github/workflows/release.yml`: [Link](https://docs.pypi.org/trusted-publishers/adding-a-publisher/) `uv publish` [doc](https://docs.astral.sh/uv/guides/publish/#publishing-your-package)