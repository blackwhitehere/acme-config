# acme-config

Layer 1 (Foundation) library. App configuration framework: schema declaration, env/CLI resolution, feature flags. Uses pydantic-settings for typed config with 12-factor env var resolution.

## Build and Test

```bash
uv sync              # Install dependencies
just test            # uv run pytest tests/ -v
just lint            # uv run ruff check src/ tests/
just format          # uv run ruff format src/ tests/
just fix             # uv run ruff check src/ tests/ --fix
```

## Architecture

- `src/acme_config/schema.py` — Config schema declaration (pydantic models)
- `src/acme_config/resolver.py` — Resolution logic (env vars, .env files, CLI)
- `src/acme_config/features.py` — Feature flag support
- `src/acme_config/inspect.py` — Config introspection utilities
- `src/acme_config/legacy/` — AWS Parameter Store code (excluded from ruff via pyproject.toml)

## Project Conventions

- Python >=3.12, ruff line-length 100, rules `["E", "F", "I", "W", "UP"]`
- `legacy/` directory is excluded from linting — contains AWS-specific code pending refactor
- No ACME dependencies — this is a foundational library
- Downstream users: `acme-prefect`, `acme-portal-sdk[prefect]`, `acme-landing`
- Pending refactor: extract AWS Parameter Store into optional extra (see `claude-context/TODO.md` #2)
