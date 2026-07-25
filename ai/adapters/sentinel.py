"""
adapters/sentinel.py
----------------------
Fetches a water-index signal (NDWI, Normalized Difference Water Index)
from Sentinel-2 imagery via the Copernicus Sentinel Hub API, and
converts it into a raw observation dict.

HONEST NOTE UP FRONT: this is the heaviest of the 3 integrations by
far. Satellite imagery isn't a simple REST GET like weather or OSM —
it needs an authenticated account, an OAuth token, and a small
"evalscript" telling Sentinel Hub what band math to run over the
image. Budget real setup time for this one; if you're tight on time
before the demo, it's reasonable to keep this on the mock/fallback
path and be upfront with judges that satellite integration is the
piece still being wired to a live account.

Setup (one-time):
  1. Create a free account at https://www.sentinel-hub.com/
     (part of Copernicus Data Space Ecosystem)
  2. In the dashboard, create an OAuth client -> get a Client ID and
     Client Secret.
  3. Set them as environment variables:
        PowerShell:  $env:SENTINELHUB_CLIENT_ID="..."
                     $env:SENTINELHUB_CLIENT_SECRET="..."
        bash:        export SENTINELHUB_CLIENT_ID="..."
                     export SENTINELHUB_CLIENT_SECRET="..."

What this returns: NDWI > ~0.3 over the queried area generally
indicates standing water. This is a coarse proxy for "is there
noticeably more surface water here than normal" — not a calibrated
flood-detection model. Treat it as a starting point, not a finished
detector; refining the NDWI threshold against real regional imagery
is a good thing to mention as "future work" to judges.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import requests

TOKEN_URL = "https://services.sentinel-hub.com/oauth/token"
PROCESS_URL = "https://services.sentinel-hub.com/api/v1/process"

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

    # The Process API returns a raw TIFF image (average NDWI per pixel).
    # Computing a true pixel-average requires a TIFF/array reader
    # (e.g. rasterio or PIL + numpy) which isn't a core dependency here
    # to keep this adapter lightweight — see NOTE below.
    #
    # NOTE: to finish this, add `pip install rasterio numpy` and:
    #   import rasterio, numpy as np, io
    #   with rasterio.io.MemoryFile(response.content) as memfile:
    #       with memfile.open() as dataset:
    #           ndwi_array = dataset.read(1)
    #   avg_ndwi = float(np.nanmean(ndwi_array))
    #
    # That avg_ndwi is what should replace the placeholder below.
    raise NotImplementedError(
        "Sentinel Hub request succeeded, but pixel decoding (TIFF -> NDWI "
        "average) needs rasterio/numpy added — see the NOTE in this "
        "function's source for the 4 lines to add. Left unfinished "
        "deliberately since it adds two extra dependencies; wire it up "
        "once you're ready to demo live imagery."
    )


def fetch_sentinel_observation_safe(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """Never-raises version — returns None on any failure, including the NotImplementedError above."""
    try:
        return fetch_sentinel_observation(lat, lon)
    except Exception:
        return None
