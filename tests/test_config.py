import pytest

from collector.config import (
    DEFAULT_API_KEY_HEADER,
    DEFAULT_TRIP_UPDATES_URL,
    DEFAULT_VEHICLES_URL,
    ConfigError,
    load_settings,
)


def test_defaults_when_only_key_is_set():
    settings = load_settings({"NTA_API_KEY": "abc"})
    assert settings.api_key == "abc"
    assert settings.api_key_header == DEFAULT_API_KEY_HEADER
    assert settings.trip_updates_url == DEFAULT_TRIP_UPDATES_URL
    assert settings.vehicles_url == DEFAULT_VEHICLES_URL
    assert settings.poll_interval_seconds == 60


@pytest.mark.parametrize("env", [{}, {"NTA_API_KEY": ""}, {"NTA_API_KEY": "   "}])
def test_missing_key_is_an_error(env):
    with pytest.raises(ConfigError, match="NTA_API_KEY"):
        load_settings(env)


def test_overrides_are_used():
    settings = load_settings(
        {
            "NTA_API_KEY": "abc",
            "NTA_API_KEY_HEADER": "Ocp-Apim-Subscription-Key",
            "NTA_TRIP_UPDATES_URL": "https://example.test/tu",
            "NTA_VEHICLES_URL": "https://example.test/v",
            "POLL_INTERVAL_SECONDS": "120",
        }
    )
    assert settings.api_key_header == "Ocp-Apim-Subscription-Key"
    assert settings.trip_updates_url == "https://example.test/tu"
    assert settings.vehicles_url == "https://example.test/v"
    assert settings.poll_interval_seconds == 120


def test_interval_below_fair_usage_limit_is_rejected():
    with pytest.raises(ConfigError, match="at least 60"):
        load_settings({"NTA_API_KEY": "abc", "POLL_INTERVAL_SECONDS": "30"})


def test_non_numeric_interval_is_rejected():
    with pytest.raises(ConfigError, match="whole number"):
        load_settings({"NTA_API_KEY": "abc", "POLL_INTERVAL_SECONDS": "soon"})
