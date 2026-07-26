"""
Simple data ingestion pipeline.
<<<<<<< HEAD
Now wired to the real AI/ML confidence engine (ai/model.py).
This file's job (Member 2 / Backend) is: collect -> clean -> store -> score.
=======
This file's job (Member 2 / Backend) is: collect -> clean -> store,
then hand sources to the AI/ML confidence engine (ai/model.py) for scoring.
>>>>>>> af87205729e166732966916dbb20e92e5c31d6ce
"""
import sys
import os

# ai/ lives at the project root, one level above backend/, so add it to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.model import run_confidence_pipeline

from sqlalchemy.orm import Session
import models

# Try to use the real AI module (ai/model.py) if it's present in the repo.
# Falls back to a simple placeholder if it isn't available yet (e.g. running
# the backend folder standalone, outside the full repo).
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


def clean_text(text: str) -> str:
    """Basic cleaning — strip whitespace, remove empty lines."""
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


def score_sources(sources: list[models.DataSource]) -> dict:
    """
<<<<<<< HEAD
    Kept for reference / fallback. No longer used by generate_insight.
    """
    count = len(sources_text)
=======
    Send sources to the real AI confidence engine (ai/model.py) and normalize
    its response into the shape the rest of the backend expects.
    Falls back to a simple placeholder if the ai/ module isn't importable
    (e.g. testing the backend folder on its own, before both are merged).
    """
    if AI_AVAILABLE:
        raw_observations = [
            {
                "source_type": s.source_type,
                "content": s.raw_content,
                "latitude": s.latitude,
                "longitude": s.longitude,
            }
            for s in sources
        ]
        result = run_confidence_pipeline(raw_observations)
        data = result.to_dict()
        # Normalize AI module's output keys to what main.py expects
        return {
            "reliability_score": data.get("reliability_score", data.get("confidence_score", 0)),
            "consistency_score": data.get("consistency_score", data.get("confidence_score", 0)),
            "confidence_score": data.get("confidence_score", 0),
            "explanation": data.get("explanation", "No explanation returned."),
        }

    # Fallback placeholder (used only if ai/ module isn't found yet)
    count = len(sources)
>>>>>>> af87205729e166732966916dbb20e92e5c31d6ce
    reliability = min(100, 60 + count * 5)
    consistency = min(100, 55 + count * 7)
    confidence = round((reliability + consistency) / 2, 1)
    explanation = f"Score derived from {count} source(s). Placeholder logic — AI module not found."
    return {
        "reliability_score": reliability,
        "consistency_score": consistency,
        "confidence_score": confidence,
        "explanation": explanation,
    }


_SOURCE_TYPE_MAP = {
    "satellite": "satellite",
    "weather": "weather",
    "osm": "osm",
    "user_report": "user_report",
    "citizen_report": "user_report",
    "news": "news",
}


def _map_source_type(source_type: str) -> str:
    return _SOURCE_TYPE_MAP.get(source_type.strip().lower(), "user_report")


def real_ai_score(sources: list) -> dict:
    """
    Real AI/ML scoring. Converts stored DataSource rows into the raw
    observation format ai/model.py expects, then runs them through the
    actual confidence pipeline (preprocessing -> scoring -> reliability
    classification -> explanation -> alert).
    """
    raw_inputs = []
    for s in sources:
        obs = {
            "source": _map_source_type(s.source_type),
            "signal": s.raw_content,
        }
        if s.latitude is not None and s.longitude is not None:
            obs["location"] = [s.latitude, s.longitude]
        raw_inputs.append(obs)

    result = run_confidence_pipeline(raw_inputs)
    data = result.to_dict()

    reliability_map = {"Low": 40, "Medium": 60, "High": 80, "Very High": 95}
    reliability_score = reliability_map.get(data["reliability"], 50)

    total = len(data["contributing_sources"]) + len(data["conflicting_sources"])
    consistency_score = (
        round(100 * len(data["contributing_sources"]) / total, 1)
        if total else data["confidence_score"]
    )

    return {
        "reliability_score": reliability_score,
        "consistency_score": consistency_score,
        "confidence_score": data["confidence_score"],
        "explanation": data["explanation"],
    }