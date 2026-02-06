# acme-config

**ALWAYS** reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

acme-config is a Python CLI tool for managing AWS Parameter Store configurations. It stores application configurations as immutable parameter sets identified by (app-name, env, ver-number) combinations and provides commands to fetch, set, and manage default versions.

## Working Effectively

### Bootstrap and Environment Setup
- Install uv package manager: `pip install uv`
- Make environment script executable: `chmod +x create_env.sh`
- Create virtual environment: `./create_env.sh` -- takes 30-45 seconds. NEVER CANCEL.
- Activate environment: `source .venv/bin/activate`

### Build and Test Commands
- Run tests: `uv run pytest tests` -- takes less than 1 second. Tests always pass quickly.
- Build documentation: `cd docs && uv run mkdocs build` -- takes 1-2 seconds. NEVER CANCEL.
- Build package: `uv build` -- takes 2-3 seconds with deprecation warnings (expected). NEVER CANCEL.
- Serve documentation locally: `cd docs && uv run mkdocs serve` -- serves on localhost:8000

### CLI Tool Usage
The main CLI tool is `ac` with these commands:
- `uv run ac --help` -- show main help
- `uv run ac fetch -app-name APP -env ENV -ver-number VER` -- fetch parameters from AWS
- `uv run ac set -app-name APP -env ENV -ver-number VER --params-path FILE.env` -- set parameters from .env file
- `uv run ac set-version -app-name APP -env ENV -ver-number VER` -- set default version
- `uv run ac get-version -app-name APP -env ENV` -- get default version

**IMPORTANT**: All CLI commands that interact with AWS will fail with `NoRegionError: You must specify a region` unless AWS credentials and region are configured. This is expected behavior.

## Validation

### Required AWS Setup for CLI Testing
The CLI requires AWS credentials and region configuration:
- Set AWS region: `export AWS_DEFAULT_REGION=us-east-1` (or your preferred region)
- Configure AWS credentials via one of:
  - `aws configure` (requires AWS CLI)
  - `aws sso login` (for SSO authentication)
  - Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
  - AWS profile: `export AWS_PROFILE=your-profile`

### Manual Testing Scenarios
When making changes, always test these scenarios:
1. **Environment Setup**: Run `./create_env.sh` and `source .venv/bin/activate`
2. **CLI Help**: Run `uv run ac --help` and verify all commands are listed
3. **Parameter File Creation**: Create test.env with `KEY=value` and verify CLI can read it
4. **Error Handling**: Test CLI commands without AWS credentials to verify proper error messages
5. **Tests**: Run `uv run pytest tests` to ensure no regressions
6. **Build Process**: Run `uv build` to verify package builds successfully
7. **Documentation**: Run `cd docs && uv run mkdocs build` to verify docs build

### Testing Without AWS Access
You can test CLI argument parsing and file operations without AWS:
```bash
# Create test environment file
echo "TEST_KEY=test_value" > test.env

# Test CLI help and argument validation (will show proper usage)
uv run ac set --help
uv run ac fetch --help

# Test file loading (will fail at AWS connection, which is expected)
uv run ac set -app-name test-app -env dev -ver-number 1 --params-path test.env
```

## Project Structure

### Key Directories and Files
```
├── .github/workflows/     # CI/CD pipelines (test.yml, release.yml)
├── src/acme_config/       # Main source code
│   ├── _main.py          # CLI entry point and argument parsing
│   ├── aws_parameter_store.py  # AWS SSM Parameter Store operations
│   └── __init__.py
├── tests/acme_config/     # Test files
│   └── test_main.py      # Basic test (currently just dummy test)
├── docs/                 # MkDocs documentation
│   ├── mkdocs.yml        # Documentation configuration
│   ├── docs/             # Documentation source files
│   └── site/             # Generated documentation (after build)
├── admin/                # Administrative scripts
│   └── refresh_credentials.sh  # AWS SSO login helper
├── pyproject.toml        # Python project configuration
├── uv.lock              # Dependency lockfile
├── create_env.sh        # Environment setup script
└── .python-version      # Python version specification (3.12)
```

### Common File Operations
- Main CLI logic: `src/acme_config/_main.py`
- AWS operations: `src/acme_config/aws_parameter_store.py`
- Project config: `pyproject.toml`
- Dependencies: `uv.lock`
- Tests: `tests/acme_config/test_main.py`
- Documentation config: `docs/mkdocs.yml`

## GitHub Actions and CI

### Workflows
- **test.yml**: Runs on push to main and all PRs
  - Sets up Python 3.12 via `.python-version` file
  - Installs dependencies with `uv sync --all-extras --dev`
  - Runs tests with `uv run pytest tests`
  - Builds documentation with `uv run mkdocs build`
  - Deploys docs to GitHub Pages

- **release.yml**: Runs on version tags (v*)
  - Builds package with `uv build`
  - Publishes to PyPI with `uv publish`
  - Requires "release-pypi" environment setup

### CI Validation
When making changes, ensure these CI steps pass:
- Tests: `uv run pytest tests`
- Documentation build: `cd docs && uv run mkdocs build`
- Package build: `uv build`

## Common Issues and Solutions

### Build Warnings
- `uv build` shows deprecation warnings about `tool.setuptools.license-files` - this is expected and can be ignored
- The build still succeeds and produces valid packages

### AWS Connection Errors
- CLI commands fail with "NoRegionError" without AWS configuration - this is expected
- Set `AWS_DEFAULT_REGION` environment variable for testing
- Use `aws sso login` or `aws configure` for full AWS access

### Environment Issues
- Always activate virtual environment: `source .venv/bin/activate`
- Re-run `./create_env.sh` if dependencies seem incorrect
- Check Python version with `python --version` (should be 3.12.x)

### Documentation Issues
- Run documentation commands from `docs/` directory
- Generated site appears in `docs/site/`
- Use `uv run mkdocs serve` for local development server

## Development Workflow

1. **Setup**: `chmod +x create_env.sh && ./create_env.sh && source .venv/bin/activate`
2. **Make changes**: Edit source files in `src/acme_config/`
3. **Test changes**: `uv run pytest tests`
4. **Test CLI**: Create test .env file and test CLI argument parsing
5. **Build validation**: `uv build` and `cd docs && uv run mkdocs build`
6. **Documentation**: Update docs in `docs/docs/` if needed

## Time Expectations

- Environment setup: 30-45 seconds
- Test execution: Less than 1 second
- Documentation build: 1-2 seconds
- Package build: 2-3 seconds
- All commands are fast - NEVER CANCEL unless hanging for 60+ minutes

All commands should complete quickly. If any command appears to hang for more than 2 minutes, investigate the issue rather than canceling.
