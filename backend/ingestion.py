"""
Simple data ingestion pipeline.
Now wired to the real AI/ML confidence engine (ai/model.py).
This file's job (Member 2 / Backend) is: collect -> clean -> store -> score.
"""
import sys
import os

# ai/ lives at the project root, one level above backend/, so add it to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.model import run_confidence_pipeline

from sqlalchemy.orm import Session
import models


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


def fake_ai_score(sources_text: list[str]) -> dict:
    """
    Kept for reference / fallback. No longer used by generate_insight.
    """
    count = len(sources_text)
    reliability = min(100, 60 + count * 5)
    consistency = min(100, 55 + count * 7)
    confidence = round((reliability + consistency) / 2, 1)
    explanation = f"Score derived from {count} source(s). Placeholder logic — swap for real AI model."
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