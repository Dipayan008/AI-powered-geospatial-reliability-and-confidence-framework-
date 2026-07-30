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


_INDIAN_STATES_AND_UTS = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
    "West Bengal", "Andaman and Nicobar Islands", "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir",
    "Ladakh", "Lakshadweep", "Puducherry",
]
# Longest names first so "Uttar Pradesh" doesn't get shadowed by "Uttarakhand"-style substrings.
_INDIAN_STATES_AND_UTS.sort(key=len, reverse=True)


def reconcile_title_with_state(title: str, state: str | None) -> str:
    """
    If a title names an Indian state/UT (e.g. "Assam Live Sensor Monitoring")
    that doesn't match the reverse-geocoded state for the insight's actual
    coordinates, swap in the correct one. This is what stops a title typed
    or guessed at ingestion time from silently disagreeing with the real
    location shown elsewhere on the card. Leaves the title untouched if it
    names no state, or if geocoding didn't resolve one.
    """
    if not title or not state:
        return title

    for named_state in _INDIAN_STATES_AND_UTS:
        if named_state.lower() in title.lower():
            if named_state.lower() == state.lower():
                return title  # already correct
            # Replace the mismatched state name with the real one, preserving case/rest of title.
            import re
            pattern = re.compile(re.escape(named_state), re.IGNORECASE)
            return pattern.sub(state, title, count=1)

    return title


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


_VALID_LOCAL_SOURCE_TYPES = {"satellite", "weather", "osm", "user_report", "news"}
_RELIABILITY_TO_SCORE = {"Low": 25.0, "Medium": 50.0, "High": 75.0, "Very High": 95.0}


def _normalize_source_type(source_type: str) -> str:
    """
    The seeded/scraped datasets use source_type to mean *disaster category*
    ("flood", "earthquake", "landslide") rather than *reporting medium*,
    which is what the local rule-based engine's SourceType enum expects.
    Map anything not already a valid medium onto "news" — every one of
    these seeded rows cites a structured dataset or news source, not a
    live sensor feed or first-person report.
    """
    key = (source_type or "").strip().lower().replace(" ", "_").replace("-", "_")
    if key in _VALID_LOCAL_SOURCE_TYPES:
        return key
    return "news"


def _local_fallback_score(sources) -> dict:
    """
    Rule-based confidence scoring (ai/model.py) — no API key, no quota,
    no external network call. Used when Gemini fails for any reason, so
    a temporary or exhausted quota never actually stops real scoring
    from happening; it just stops the LLM-written explanation from
    happening, which is the honest trade-off to make here.
    """
    raw_observations = [
        {
            "source": _normalize_source_type(s.source_type),
            "signal": s.raw_content,
            "location": [s.latitude, s.longitude] if s.latitude is not None and s.longitude is not None else None,
            "timestamp": s.fetched_at.isoformat() if getattr(s, "fetched_at", None) else None,
        }
        for s in sources
    ]

    result = run_confidence_pipeline(raw_observations)
    payload = result.to_dict()

    total = len(payload["contributing_sources"]) + len(payload["conflicting_sources"])
    consistency = round(100 * len(payload["contributing_sources"]) / total, 1) if total else 0.0

    return {
        "reliability_score": _RELIABILITY_TO_SCORE.get(payload["reliability"], 0.0),
        "consistency_score": consistency,
        "confidence_score": payload["confidence_score"],
        "explanation": (
            "(Gemini unavailable — scored by local rule-based engine instead) "
            f"{payload['explanation']}"
        ),
    }


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
        # The pipeline must never crash if the Gemini call fails (rate limit,
        # quota exhaustion, network error, malformed response, etc.) — but it
        # also must never present that failure as if it were a real "0%,
        # Low risk" assessment, and must never leak the raw SDK exception
        # text (which can include quota numbers, links, internal metric
        # names) into a citizen-facing explanation field.
        error_str = str(e)
        is_rate_limit = "429" in error_str or "quota" in error_str.lower()
        reason = (
            "the AI scoring service's request quota was reached"
            if is_rate_limit
            else "the AI scoring service returned an error"
        )
        return {
            "reliability_score": 0,
            "consistency_score": 0,
            "confidence_score": 0,
            "explanation": (
                f"AI_SCORING_UNAVAILABLE: Scoring could not be completed because {reason}. "
                "This is not an assessed result — retry once the service is available."
            ),
        }

def score_sources(sources) -> dict:
    """
    Adapter for main.py, which expects a `score_sources(sources)` function.
    `sources` here are DataSource model objects (from the database).

    Tries Gemini first (richer, LLM-written explanations). If that fails
    for any reason (rate limit, quota, network, malformed response) and
    the local rule-based engine is available, falls back to that instead
    of returning a fake/unavailable result — so scoring keeps working
    even with Gemini's free-tier quota exhausted.
    """
    texts = [s.raw_content for s in sources]
    result = fake_ai_score(texts)

    gemini_failed = result["explanation"].startswith("AI_SCORING_UNAVAILABLE:")
    if gemini_failed and AI_AVAILABLE:
        try:
            return _local_fallback_score(sources)
        except Exception:
            # Local engine itself failed too (e.g. no usable observations) —
            # surface the original honest "unavailable" result rather than
            # a second, different failure.
            return result

    return result
