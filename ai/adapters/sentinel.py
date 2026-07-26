"""
adapters/sentinel.py
----------------------
Fetches a water-index signal (NDWI, Normalized Difference Water Index)
from Sentinel-2 imagery via the Copernicus Data Space Ecosystem's
Sentinel Hub-compatible API, and converts it into a raw observation dict.

IMPORTANT: use dataspace.copernicus.eu, NOT sentinel-hub.com directly.
The commercial sentinel-hub.com site defaults to a 30-day paid trial.
The Copernicus Data Space Ecosystem is the official ESA/EU portal and
offers genuinely free API access (with usage quotas, no credit card)
to the same underlying Sentinel Hub Process API — that's what this
adapter is built against.

Setup (one-time, free, no card required):
  1. Register a free account at https://dataspace.copernicus.eu/
  2. Log in, go to your user dashboard -> Sentinel Hub -> "Manage your
     account" / OAuth clients section, and create an OAuth client.
     Copy the Client ID and Client Secret it gives you.
  3. Set them as environment variables:
        PowerShell:  $env:SENTINELHUB_CLIENT_ID="..."
                     $env:SENTINELHUB_CLIENT_SECRET="..."
        bash:        export SENTINELHUB_CLIENT_ID="..."
                     export SENTINELHUB_CLIENT_SECRET="..."
  4. pip install rasterio numpy (in addition to requirements.txt)

What this returns: NDWI > ~0.3 over the queried area generally
indicates standing water. This is a coarse proxy for "is there
noticeably more surface water here than normal" — not a calibrated
flood-detection model. Treat it as a starting point; refining the NDWI
threshold against real regional imagery, or comparing against a
recent historical baseline for the same location, is good "future
work" to mention to judges.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import requests

# Copernicus Data Space Ecosystem endpoints (free tier) — NOT
# services.sentinel-hub.com, which is the paid commercial product.
TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
PROCESS_URL = "https://sh.dataspace.copernicus.eu/process/v1"

# Simple NDWI evalscript: (Green - NIR) / (Green + NIR), averaged over
# the queried bounding box. B03 = green, B08 = near-infrared for Sentinel-2.
_NDWI_EVALSCRIPT = """
//VERSION=3
function setup() {
  return {
    input: ["B03", "B08"],
    output: { bands: 1, sampleType: "FLOAT32" }
  };
}
function evaluatePixel(sample) {
  let ndwi = (sample.B03 - sample.B08) / (sample.B03 + sample.B08 + 0.0001);
  return [ndwi];
}
"""

NDWI_WATER_THRESHOLD = 0.3


def _get_access_token(client_id: str, client_secret: str, timeout: float = 10.0) -> str:
    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def _bbox_around(lat: float, lon: float, half_size_deg: float = 0.02):
    # Roughly a ~2-4km box depending on latitude — fine-grained enough
    # for a single reported location, coarse enough to tolerate GPS drift.
    return [lon - half_size_deg, lat - half_size_deg, lon + half_size_deg, lat + half_size_deg]


def fetch_sentinel_observation(
    lat: float,
    lon: float,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    timeout: float = 30.0,
) -> Dict[str, Any]:
    """
    Returns a raw observation dict based on average NDWI over a small
    area around (lat, lon) in the most recent available Sentinel-2 pass:

        {"source": "satellite", "signal": "flood_detected" | "no_flood_signal",
         "location": [lat, lon], "timestamp": "...", "confidence": ...}
    """
    import os

    cid = client_id or os.environ.get("SENTINELHUB_CLIENT_ID")
    secret = client_secret or os.environ.get("SENTINELHUB_CLIENT_SECRET")
    if not cid or not secret:
        raise ValueError(
            "Missing Sentinel Hub credentials. Set SENTINELHUB_CLIENT_ID and "
            "SENTINELHUB_CLIENT_SECRET (see adapters/sentinel.py docstring for setup)."
        )

    token = _get_access_token(cid, secret, timeout=timeout)
    bbox = _bbox_around(lat, lon)

    now = datetime.now(timezone.utc)
    time_range = {
        "from": (now - timedelta(days=10)).strftime("%Y-%m-%dT00:00:00Z"),
        "to": now.strftime("%Y-%m-%dT23:59:59Z"),
    }

    payload = {
        "input": {
            "bounds": {"bbox": bbox},
            "data": [{
                "type": "sentinel-2-l2a",
                "dataFilter": {"timeRange": time_range, "maxCloudCoverage": 40},
            }],
        },
        "output": {"width": 64, "height": 64, "responses": [{"identifier": "default", "format": {"type": "image/tiff"}}]},
        "evalscript": _NDWI_EVALSCRIPT,
    }

    response = requests.post(
        PROCESS_URL,
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
        timeout=timeout,
    )
    response.raise_for_status()

    # The Process API returns a raw single-band TIFF (NDWI per pixel).
    # Decode it and average across the queried area to get one number.
    import io
    import numpy as np
    import rasterio

    with rasterio.io.MemoryFile(response.content) as memfile:
        with memfile.open() as dataset:
            ndwi_array = dataset.read(1)

    avg_ndwi = float(np.nanmean(ndwi_array))
    signal = "flood_detected" if avg_ndwi >= NDWI_WATER_THRESHOLD else "no_flood_signal"

    # Map how far above/below the threshold we are into a rough 0-1
    # confidence — further from the threshold in either direction means
    # a clearer (less ambiguous) reading.
    distance_from_threshold = abs(avg_ndwi - NDWI_WATER_THRESHOLD)
    confidence = min(0.95, 0.6 + distance_from_threshold)

    return {
        "source": "satellite",
        "signal": signal,
        "location": [lat, lon],
        "timestamp": now.isoformat(),
        "confidence": round(confidence, 2),
        "raw": {"avg_ndwi": round(avg_ndwi, 4), "threshold": NDWI_WATER_THRESHOLD},
    }


def fetch_sentinel_observation_safe(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """Never-raises version — returns None on any failure, including the NotImplementedError above."""
    try:
        return fetch_sentinel_observation(lat, lon)
    except Exception:
        return None
