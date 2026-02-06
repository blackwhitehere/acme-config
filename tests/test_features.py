"""Tests for feature flags."""

from acme_config.features import FeatureFlag, FeatureFlags, list_flags


class SampleFeatures(FeatureFlags):
    model_config = {"env_prefix": "MYAPP_FEATURE_"}

    new_dashboard: bool = FeatureFlag(default=False, description="Enable new dashboard")
    parallel: bool = FeatureFlag(default=True, description="Use parallel processing")


class TestFeatureFlags:
    def test_defaults(self):
        flags = SampleFeatures()
        assert flags.new_dashboard is False
        assert flags.parallel is True

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("MYAPP_FEATURE_NEW_DASHBOARD", "true")
        flags = SampleFeatures()
        assert flags.new_dashboard is True

    def test_is_enabled(self):
        flags = SampleFeatures()
        assert flags.is_enabled("new_dashboard") is False
        assert flags.is_enabled("parallel") is True

    def test_is_enabled_missing_flag(self):
        flags = SampleFeatures()
        try:
            flags.is_enabled("nonexistent")
            assert False, "Should have raised AttributeError"
        except AttributeError:
            pass

    def test_env_false(self, monkeypatch):
        monkeypatch.setenv("MYAPP_FEATURE_PARALLEL", "false")
        flags = SampleFeatures()
        assert flags.parallel is False


class TestListFlags:
    def test_list_all_flags(self):
        flags = SampleFeatures()
        result = list_flags(flags)
        assert len(result) == 2

        names = {f["name"] for f in result}
        assert names == {"new_dashboard", "parallel"}

    def test_flag_values(self, monkeypatch):
        monkeypatch.setenv("MYAPP_FEATURE_NEW_DASHBOARD", "true")
        flags = SampleFeatures()
        result = list_flags(flags)

        dashboard = next(f for f in result if f["name"] == "new_dashboard")
        assert dashboard["value"] is True
        assert dashboard["default"] is False
        assert dashboard["description"] == "Enable new dashboard"
