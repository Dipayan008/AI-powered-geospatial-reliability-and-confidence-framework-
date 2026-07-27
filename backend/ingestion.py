"""
Simple data ingestion pipeline.
Member 3 (AI/ML) will later replace `fake_ai_score()` with real model calls.
This file's job (Member 2 / Backend) is just: collect -> clean -> store.
"""

from sqlalchemy.orm import Session
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-flash-latest")
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