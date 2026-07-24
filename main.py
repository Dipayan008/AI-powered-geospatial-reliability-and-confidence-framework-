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

from ai.model import run_confidence_pipeline

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


@app.post("/analyze")
def analyze(payload: AnalyzeRequest) -> Dict[str, Any]:
    """
    Main endpoint: takes raw observations for one event/location cluster
    and returns confidence score, reliability, alert level, and an
    explainable-AI justification.
    """
    raw_inputs = [obs.model_dump() for obs in payload.observations]
    result = run_confidence_pipeline(raw_inputs)
    return result.to_dict()
