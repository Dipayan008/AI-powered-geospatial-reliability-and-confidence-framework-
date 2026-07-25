"""
main.py
-------
FastAPI wrapper around the AI confidence engine. This is what Member 2
(backend) can run standalone, or mount into the main backend service.

Run locally:
    pip install -r requirements.txt
    uvicorn main:app --reload

Then POST sample data:
    curl -X POST http://127.0.0.1:8000/analyze -H "Content-Type: application/json" \
         -d @sample_data.json
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ai.model import run_confidence_pipeline, run_multi_event_pipeline
from ai.adapters.openweather import fetch_weather_observation_safe
from ai.adapters.osm import fetch_osm_observation_safe
from ai.adapters.sentinel import fetch_sentinel_observation_safe

app = FastAPI(
    title="GeoTrust AI - Confidence Engine",
    description="AI framework to judge reliability, consistency & confidence "
                "of insights from multiple space & geospatial data sources (PS07).",
    version="0.1.0",
)

# Wide open for hackathon demo purposes; tighten before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Observation(BaseModel):
    source: str = Field(..., description="satellite | weather | osm | user_report | news")
    signal: str = Field(..., description="e.g. 'Flood Detected', 'Heavy Rain'")
    location: Optional[List[float]] = Field(None, description="[lat, lon]")
    timestamp: Optional[str] = None
    confidence: Optional[float] = Field(None, description="0-1, if the source reports its own confidence")


class AnalyzeRequest(BaseModel):
    observations: List[Observation]


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/analyze-live")
def analyze_live(lat: float, lon: float, extra_observations: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetches REAL data for a location (OpenWeather + OSM live; Sentinel-2
    included but currently returns no data until its TIFF decoding step
    is finished — see ai/adapters/sentinel.py) and scores it through the
    same confidence pipeline used everywhere else.

    You can still pass user reports / news manually via
    extra_observations as a JSON string, e.g.:
        /analyze-live?lat=22.57&lon=88.36&extra_observations=[{"source":"user_report","signal":"Road Under Water","location":[22.57,88.36]}]

    Any adapter that fails (bad key, rate limit, network) is silently
    skipped rather than crashing the whole request — a missing source
    just means one less data point feeding the score, which the engine
    already handles.
    """
    import json as _json

    observations: List[Dict[str, Any]] = []

    weather_obs = fetch_weather_observation_safe(lat, lon)
    if weather_obs:
        observations.append(weather_obs)

    osm_obs = fetch_osm_observation_safe(lat, lon)
    if osm_obs:
        observations.append(osm_obs)

    sentinel_obs = fetch_sentinel_observation_safe(lat, lon)
    if sentinel_obs:
        observations.append(sentinel_obs)

    if extra_observations:
        try:
            observations.extend(_json.loads(extra_observations))
        except _json.JSONDecodeError:
            pass  # malformed extra input shouldn't break the live sources we did get

    result = run_confidence_pipeline(observations)
    payload = result.to_dict()
    payload["sources_fetched"] = {
        "weather": weather_obs is not None,
        "osm": osm_obs is not None,
        "satellite": sentinel_obs is not None,
    }
    return payload


@app.post("/analyze")
def analyze(payload: AnalyzeRequest) -> Dict[str, Any]:
    """
    Single-event endpoint: takes raw observations that are ALL believed
    to be about one event/location cluster, and returns one confidence
    result. Use this when your frontend has already grouped the
    observations (e.g. "everything reported about this one flood").
    """
    raw_inputs = [obs.model_dump() for obs in payload.observations]
    result = run_confidence_pipeline(raw_inputs)
    return result.to_dict()


@app.post("/analyze-batch")
def analyze_batch(payload: AnalyzeRequest) -> Dict[str, Any]:
    """
    Multi-event endpoint: takes a mixed batch of raw observations that
    may describe SEVERAL different, unrelated events/locations at once
    (the realistic case for a live monitoring feed). Clusters them by
    location + time proximity first, then scores each event
    independently.
    """
    raw_inputs = [obs.model_dump() for obs in payload.observations]
    results = run_multi_event_pipeline(raw_inputs)
    return {"events": [r.to_dict() for r in results], "event_count": len(results)}
