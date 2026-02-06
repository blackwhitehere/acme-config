"""Tests for config inspection utilities."""

from acme_config.inspect import (
    describe_config,
    generate_dotenv_template,
    generate_manifest,
    validate_env,
)
from acme_config.schema import AppConfig, ConfigField


class InspectableConfig(AppConfig):
    model_config = {"env_prefix": "INS_"}

    name: str = ConfigField(description="App name")
    port: int = ConfigField(default=8080, description="Port")
    api_key: str = ConfigField(default="", description="API key", secret=True)


class TestGenerateManifest:
    def test_includes_all_fields(self):
        manifest = generate_manifest(InspectableConfig)
        assert "INS_NAME" in manifest
        assert "INS_PORT" in manifest
        assert "INS_API_KEY" in manifest

    def test_marks_required(self):
        manifest = generate_manifest(InspectableConfig)
        lines = manifest.splitlines()
        name_line = next(line for line in lines if "INS_NAME" in line)
        assert "required" in name_line

    def test_marks_secret(self):
        manifest = generate_manifest(InspectableConfig)
        lines = manifest.splitlines()
        key_line = next(line for line in lines if "INS_API_KEY" in line)
        assert "secret" in key_line


class TestGenerateDotenvTemplate:
    def test_generates_template(self):
        template = generate_dotenv_template(InspectableConfig)
        assert "INS_NAME=" in template
        assert "INS_PORT" in template

    def test_required_fields_empty(self):
        template = generate_dotenv_template(InspectableConfig)
        # Required field should have empty value (no default)
        assert "INS_NAME=" in template

    def test_optional_fields_commented(self):
        template = generate_dotenv_template(InspectableConfig)
        # Fields with defaults should be commented out
        lines = template.splitlines()
        port_line = next(
            line for line in lines
            if "INS_PORT" in line and "description" not in line.lower()
        )
        assert port_line.startswith("#")


class TestValidateEnv:
    def test_missing_required(self, monkeypatch):
        monkeypatch.delenv("INS_NAME", raising=False)
        issues = validate_env(InspectableConfig)
        assert len(issues) > 0

    def test_all_present(self, monkeypatch):
        monkeypatch.setenv("INS_NAME", "test")
        issues = validate_env(InspectableConfig)
        assert len(issues) == 0


class TestDescribeConfig:
    def test_shows_values(self, monkeypatch):
        monkeypatch.setenv("INS_NAME", "myapp")
        config = InspectableConfig()
        desc = describe_config(config)
        assert "myapp" in desc
        assert "8080" in desc

    def test_redacts_secrets(self, monkeypatch):
        monkeypatch.setenv("INS_NAME", "myapp")
        monkeypatch.setenv("INS_API_KEY", "sk-super-secret")
        config = InspectableConfig()
        desc = describe_config(config)
        assert "sk-super-secret" not in desc
        assert "***" in desc

    def test_includes_class_name(self, monkeypatch):
        monkeypatch.setenv("INS_NAME", "myapp")
        config = InspectableConfig()
        desc = describe_config(config)
        assert "InspectableConfig" in desc
