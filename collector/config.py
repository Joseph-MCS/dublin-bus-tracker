"""Collector settings, read from environment variables."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

DEFAULT_TRIP_UPDATES_URL = "https://api.nationaltransport.ie/gtfsr/v2/TripUpdates"
# Not yet confirmed against the NTA developer portal; override with NTA_VEHICLES_URL.
DEFAULT_VEHICLES_URL = "https://api.nationaltransport.ie/gtfsr/v2/Vehicles"
DEFAULT_API_KEY_HEADER = "x-api-key"

# NTA fair-usage policy: each key may call the GTFS-R API at most once every 60 seconds.
MIN_POLL_INTERVAL_SECONDS = 60


class ConfigError(ValueError):
    """Raised when the collector's settings are missing or invalid."""


@dataclass(frozen=True)
class Settings:
    api_key: str
    api_key_header: str
    trip_updates_url: str
    vehicles_url: str
    poll_interval_seconds: int


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """Build settings from ``env`` (defaults to ``os.environ``)."""
    env = os.environ if env is None else env

    api_key = env.get("NTA_API_KEY", "").strip()
    if not api_key:
        raise ConfigError(
            "NTA_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    raw_interval = env.get("POLL_INTERVAL_SECONDS", str(MIN_POLL_INTERVAL_SECONDS))
    try:
        interval = int(raw_interval)
    except ValueError:
        raise ConfigError(
            f"POLL_INTERVAL_SECONDS must be a whole number, got {raw_interval!r}."
        ) from None
    if interval < MIN_POLL_INTERVAL_SECONDS:
        raise ConfigError(
            f"POLL_INTERVAL_SECONDS must be at least {MIN_POLL_INTERVAL_SECONDS} "
            "(NTA fair-usage limit)."
        )

    return Settings(
        api_key=api_key,
        api_key_header=env.get("NTA_API_KEY_HEADER") or DEFAULT_API_KEY_HEADER,
        trip_updates_url=env.get("NTA_TRIP_UPDATES_URL") or DEFAULT_TRIP_UPDATES_URL,
        vehicles_url=env.get("NTA_VEHICLES_URL") or DEFAULT_VEHICLES_URL,
        poll_interval_seconds=interval,
    )
