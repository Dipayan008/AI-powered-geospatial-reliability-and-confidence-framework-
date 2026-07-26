"""
Simple data ingestion pipeline.
This file's job (Member 2 / Backend) is: collect -> clean -> store,
then hand sources to the AI/ML confidence engine (ai/model.py) for scoring.
"""

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
