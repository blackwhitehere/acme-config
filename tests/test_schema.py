"""Tests for AppConfig schema declaration and resolution."""

import pytest

from acme_config.resolver import build_cli_parser, resolve_config
from acme_config.schema import AppConfig, ConfigField


class SampleConfig(AppConfig):
    model_config = {"env_prefix": "SAMPLE_"}

    name: str = ConfigField(description="App name", cli_flag="--name")
    port: int = ConfigField(default=8080, description="Port number", cli_flag="--port")
    debug: bool = ConfigField(default=False, description="Debug mode", cli_flag="--debug")
    db_password: str = ConfigField(default="", description="DB password", secret=True)


class TestAppConfig:
    def test_defaults(self):
        config = SampleConfig(name="test")
        assert config.name == "test"
        assert config.port == 8080
        assert config.debug is False
        assert config.db_password == ""

    def test_env_vars_override_defaults(self, monkeypatch):
        monkeypatch.setenv("SAMPLE_NAME", "from-env")
        monkeypatch.setenv("SAMPLE_PORT", "9090")
        config = SampleConfig()
        assert config.name == "from-env"
        assert config.port == 9090

    def test_env_file_loading(self, tmp_path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text("SAMPLE_NAME=from-file\nSAMPLE_PORT=3000\n")
        # Clear env vars so file takes effect
        monkeypatch.delenv("SAMPLE_NAME", raising=False)
        monkeypatch.delenv("SAMPLE_PORT", raising=False)
        config = SampleConfig(_env_file=str(env_file))
        assert config.name == "from-file"
        assert config.port == 3000

    def test_env_var_overrides_file(self, tmp_path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text("SAMPLE_NAME=from-file\n")
        monkeypatch.setenv("SAMPLE_NAME", "from-env")
        config = SampleConfig(_env_file=str(env_file))
        assert config.name == "from-env"


class TestResolveConfig:
    def test_basic_resolve(self, monkeypatch):
        monkeypatch.setenv("SAMPLE_NAME", "resolved")
        config = resolve_config(SampleConfig)
        assert config.name == "resolved"

    def test_cli_args_override_env(self, monkeypatch):
        monkeypatch.setenv("SAMPLE_NAME", "from-env")
        monkeypatch.setenv("SAMPLE_PORT", "1111")
        config = resolve_config(SampleConfig, cli_args={"port": "9999"})
        assert config.name == "from-env"
        assert config.port == 9999

    def test_cli_none_values_skipped(self, monkeypatch):
        monkeypatch.setenv("SAMPLE_NAME", "env-val")
        config = resolve_config(SampleConfig, cli_args={"name": None})
        assert config.name == "env-val"

    def test_overrides_highest_priority(self, monkeypatch):
        monkeypatch.setenv("SAMPLE_NAME", "from-env")
        config = resolve_config(
            SampleConfig,
            cli_args={"name": "from-cli"},
            overrides={"name": "from-override"},
        )
        assert config.name == "from-override"

    def test_custom_env_file(self, tmp_path, monkeypatch):
        env_file = tmp_path / "custom.env"
        env_file.write_text("SAMPLE_NAME=custom\n")
        monkeypatch.delenv("SAMPLE_NAME", raising=False)
        config = resolve_config(SampleConfig, env_file=str(env_file))
        assert config.name == "custom"


class TestBuildCliParser:
    def test_generates_arguments(self):
        parser = build_cli_parser(SampleConfig)
        args = parser.parse_args(["--name", "myapp", "--port", "3000"])
        assert args.name == "myapp"
        assert args.port == "3000"

    def test_debug_flag(self):
        parser = build_cli_parser(SampleConfig)
        args = parser.parse_args(["--name", "x", "--debug"])
        assert args.debug is True

    def test_no_flag_fields_without_cli_flag(self):
        """Fields without cli_flag should not appear in parser."""
        parser = build_cli_parser(SampleConfig)
        # db_password has no cli_flag, so --db-password should not work
        with pytest.raises(SystemExit):
            parser.parse_args(["--db-password", "secret"])

    def test_integration_with_resolve(self, monkeypatch):
        monkeypatch.setenv("SAMPLE_NAME", "env-name")
        parser = build_cli_parser(SampleConfig)
        args = parser.parse_args(["--port", "4000"])
        config = resolve_config(SampleConfig, cli_args=vars(args))
        assert config.name == "env-name"
        assert config.port == 4000
