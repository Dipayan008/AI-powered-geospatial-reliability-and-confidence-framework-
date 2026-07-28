"""
Simple data ingestion pipeline.
This file's job (Member 2 / Backend) is: collect -> clean -> store,
then hand sources to the AI/ML confidence engine (ai/model.py) for scoring.
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-flash-latest")
import models
import requests

try:
    from ai.model import run_confidence_pipeline
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

try:
    from ai.model import run_multi_event_pipeline
    MULTI_EVENT_AVAILABLE = True
except ImportError:
    MULTI_EVENT_AVAILABLE = False

try:
    from ai.adapters.openweather import fetch_weather_observation_safe
    from ai.adapters.osm import fetch_osm_observation_safe
    from ai.adapters.sentinel import fetch_sentinel_observation_safe
    LIVE_ADAPTERS_AVAILABLE = True
except ImportError:
    LIVE_ADAPTERS_AVAILABLE = False


def fetch_live_weather_safe(lat: float, lon: float):
    if not LIVE_ADAPTERS_AVAILABLE:
        return None
    return fetch_weather_observation_safe(lat, lon)


def fetch_live_osm_safe(lat: float, lon: float):
    if not LIVE_ADAPTERS_AVAILABLE:
        return None
    return fetch_osm_observation_safe(lat, lon)


def fetch_live_sentinel_safe(lat: float, lon: float):
    if not LIVE_ADAPTERS_AVAILABLE:
        return None
    return fetch_sentinel_observation_safe(lat, lon)


def reverse_geocode_safe(lat: float, lon: float, timeout: float = 10.0):
    """
    Reverse-geocodes a lat/lon into town/district/state names using
    OpenStreetMap's free Nominatim API (no API key required).
    Returns None on any failure (network error, rate limit, no results)
    rather than raising, so a geocoding hiccup never breaks an insight.
    """
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json"},
            headers={"User-Agent": "PS07-GeoAI-Hackathon-Project"},
            timeout=timeout,
        )
        response.raise_for_status()
        data = response.json()
        address = data.get("address", {})

        town = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("suburb")
        )
        district = address.get("state_district") or address.get("county")
        state = address.get("state")

        if not any([town, district, state]):
            return None

        return {
            "town_village": town,
            "district": district,
            "state": state,
        }
    except Exception:
        return None


def clean_text(text: str) -> str:
    """Basic cleaning: strip whitespace, remove empty lines."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def ingest_source(db: Session, name: str, source_type: str, raw_content: str,
                   latitude: float = None, longitude: float = None) -> models.DataSource:
    """Store one incoming data source record after basic cleaning."""
    cleaned = clean_text(raw_content)
    source = models.DataSource(
        name=name,
        source_type=source_type,
        raw_content=cleaned,
        latitude=latitude,
        longitude=longitude,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


def fake_ai_score(sources_text: list[str]) -> dict:
    """
    Calls Gemini to assess reliability/consistency of the given sources.
    Keeps the same return shape as the original placeholder so nothing
    downstream (main.py, etc.) needs to change.
    """
    count = len(sources_text)
    joined_sources = "\n---\n".join(sources_text)

    prompt = f"""
You are assessing the reliability of {count} disaster/hazard report(s) below.
Sources:
{joined_sources}

Return ONLY a JSON object with these exact keys, no other text:
{{
  "reliability_score": <number 0-100>,
  "consistency_score": <number 0-100>,
  "confidence_score": <number 0-100>,
  "explanation": "<short explanation of the score>"
}}
"""

    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()
        # Strip markdown code fences if Gemini wraps the JSON in ```json ... ```
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        return result
    except Exception as e:
        # Fallback so the pipeline never crashes if the API call fails
        return {
            "reliability_score": 0,
            "consistency_score": 0,
            "confidence_score": 0,
            "explanation": f"AI scoring failed: {str(e)}",
        }

def score_sources(sources) -> dict:
    """
    Adapter for main.py, which expects a `score_sources(sources)` function.
    `sources` here are DataSource model objects (from the database),
    not raw strings — so we pull out their text content first.
    """
    texts = [s.raw_content for s in sources]
    return fake_ai_score(texts)
