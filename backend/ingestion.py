"""
Simple data ingestion pipeline.
Member 3 (AI/ML) will later replace `fake_ai_score()` with real model calls.
This file's job (Member 2 / Backend) is just: collect -> clean -> store.
"""

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
    Placeholder scoring logic so the backend/frontend can be built and demoed
    before Member 3's real AI model is plugged in.
    Replace this function's internals with the real call to the AI engine.
    """
    # naive placeholder: more sources agreeing roughly in length/content = more "consistent"
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
