"""
adapters/openweather.py
------------------------
Fetches real current-weather data from OpenWeather and converts it
into the raw observation dict shape the confidence engine expects.

Get a free API key at: https://openweathermap.org/api
Set it as an environment variable:

    PowerShell:  $env:OPENWEATHER_API_KEY="your-key-here"
    bash:        export OPENWEATHER_API_KEY="your-key-here"

Usage:
    from ai.adapters.openweather import fetch_weather_observation
    obs = fetch_weather_observation(22.5726, 88.3639)
    # obs is a dict ready to pass straight into run_confidence_pipeline([obs, ...])
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import requests

OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# OpenWeather condition codes: https://openweathermap.org/weather-conditions
# Group 2xx = thunderstorm, 3xx = drizzle, 5xx = rain, 6xx = snow, 800 = clear.
_HEAVY_RAIN_CODES = range(500, 532)   # rain + thunderstorm variants
_CLEAR_CODES = {800, 801}             # clear / few clouds -> "no rain"


def _classify_condition(weather_code: int, rain_1h_mm: float) -> str:
    """
    Turn OpenWeather's numeric condition code + rainfall volume into a
    signal string the confidence engine understands (see
    utils.infer_polarity for how "no_rain" etc. get treated as a denial).
    """
    if rain_1h_mm >= 20 or weather_code in range(502, 505) or weather_code in range(202, 203):
        return "heavy_rain"
    if weather_code in _HEAVY_RAIN_CODES or rain_1h_mm > 0:
        return "rain"
    if weather_code in _CLEAR_CODES:
        return "no_rain"
    return "normal_weather"


def fetch_weather_observation(
    lat: float,
    lon: float,
    api_key: Optional[str] = None,
    timeout: float = 8.0,
) -> Dict[str, Any]:
    """
    Fetch current weather for a location and return it as a raw
    observation dict, e.g.:

        {"source": "weather", "signal": "heavy_rain",
         "location": [22.5726, 88.3639], "timestamp": "...",
         "confidence": 0.9}

    Raises requests.RequestException on network failure — callers
    should catch this and fall back gracefully (see fetch_safely
    below) rather than let one flaky API call kill the whole pipeline.
    """
    key = api_key or os.environ.get("OPENWEATHER_API_KEY")
    if not key:
        raise ValueError(
            "No OpenWeather API key found. Set OPENWEATHER_API_KEY in your "
            "environment or pass api_key= explicitly."
        )

    params = {"lat": lat, "lon": lon, "appid": key, "units": "metric"}
    response = requests.get(OPENWEATHER_BASE_URL, params=params, timeout=timeout)
    response.raise_for_status()
    data = response.json()

    weather_code = data.get("weather", [{}])[0].get("id", 800)
    rain_1h_mm = data.get("rain", {}).get("1h", 0.0)
    signal = _classify_condition(weather_code, rain_1h_mm)

    return {
        "source": "weather",
        "signal": signal,
        "location": [lat, lon],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        # A simple confidence heuristic: heavier/clearer readings get
        # slightly higher confidence than ambiguous mid-range ones.
        "confidence": 0.9 if signal in ("heavy_rain", "no_rain") else 0.75,
        "raw": {"weather_code": weather_code, "rain_1h_mm": rain_1h_mm},
    }


def fetch_weather_observation_safe(lat: float, lon: float, api_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Same as fetch_weather_observation, but never raises — returns None
    on any failure (bad key, no network, rate limit) so a live-demo
    call to this adapter can't crash the whole request. Log the error
    yourself if you want visibility into why it returned None.
    """
    try:
        return fetch_weather_observation(lat, lon, api_key=api_key)
    except Exception:
        return None
