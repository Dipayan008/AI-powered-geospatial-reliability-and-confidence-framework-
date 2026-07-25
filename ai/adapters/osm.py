"""
adapters/osm.py
----------------
Queries OpenStreetMap's Overpass API (no API key needed) for known
geography near a location — mainly to check whether a "flood" report
is even near a plausible flood-prone feature (a river, low-lying road,
drainage channel), which is the kind of context OSM is actually good
for. OSM is NOT a real-time data source — it won't tell you a flood is
happening right now — so its role in the pipeline is corroborating
context, not a primary confirm/deny signal.

Usage:
    from ai.adapters.osm import fetch_osm_observation
    obs = fetch_osm_observation(22.5726, 88.3639)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
SEARCH_RADIUS_METERS = 500


def _build_query(lat: float, lon: float, radius_m: int) -> str:
    # Looks for waterways, riverbanks, and low-lying roads within radius_m
    # of the point — a rough proxy for "is this a place floods plausibly happen".
    return f"""
    [out:json][timeout:10];
    (
      way["waterway"](around:{radius_m},{lat},{lon});
      way["natural"="water"](around:{radius_m},{lat},{lon});
      way["highway"](around:{radius_m},{lat},{lon});
    );
    out center 10;
    """


def fetch_osm_observation(
    lat: float,
    lon: float,
    radius_m: int = SEARCH_RADIUS_METERS,
    timeout: float = 15.0,
) -> Dict[str, Any]:
    """
    Returns a raw observation dict describing whether flood-relevant
    geography (waterways, low-lying roads) exists near this point.

        {"source": "osm", "signal": "waterway_nearby" | "no_waterway_nearby",
         "location": [lat, lon], "timestamp": "..."}
    """
    query = _build_query(lat, lon, radius_m)
    response = requests.post(OVERPASS_URL, data={"data": query}, timeout=timeout)
    response.raise_for_status()
    data = response.json()

    elements = data.get("elements", [])
    has_waterway = any(
        "waterway" in el.get("tags", {}) or el.get("tags", {}).get("natural") == "water"
        for el in elements
    )

    signal = "waterway_nearby" if has_waterway else "no_waterway_nearby"

    return {
        "source": "osm",
        "signal": signal,
        "location": [lat, lon],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "raw": {"feature_count": len(elements)},
    }


def fetch_osm_observation_safe(lat: float, lon: float, radius_m: int = SEARCH_RADIUS_METERS) -> Optional[Dict[str, Any]]:
    """Never-raises version — returns None on any failure (rate limit, timeout, etc.)."""
    try:
        return fetch_osm_observation(lat, lon, radius_m=radius_m)
    except Exception:
        return None
