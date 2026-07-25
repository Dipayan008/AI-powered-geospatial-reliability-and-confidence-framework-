"""
model.py
--------
The single public entry point for the AI/ML module. This is what your
backend teammate (Member 2) actually imports and calls — they don't
need to know about preprocessing, scoring, or Gemini internals.

    from ai.model import run_confidence_pipeline
    result = run_confidence_pipeline(raw_reports)
    result.to_dict()  # -> JSON-ready dict for the FastAPI response
"""

from __future__ import annotations

from typing import Any, Dict, List

from .confidence_engine import score_event
from .explanation import generate_explanation
from .prediction import predict_alert
from .preprocessing import preprocess
from .reliability import classify_reliability
from .clustering import cluster_observations
from .utils import ConfidenceResult, SourceObservation


def _pick_representative_location(observations: List[SourceObservation]):
    for obs in observations:
        if obs.location:
            return obs.location
    return None


def run_confidence_pipeline(raw_inputs: List[Dict[str, Any]]) -> ConfidenceResult:
    """
    Full pipeline: preprocess -> score -> classify -> explain -> alert.

    Args:
        raw_inputs: list of raw observation dicts from satellite,
            weather, OSM, user reports, and/or news for ONE
            event/location cluster (e.g. everything reported about a
            single flood in the last hour).

    Returns:
        A ConfidenceResult ready to serialize with .to_dict().
    """
    observations = preprocess(raw_inputs)

    if not observations:
        return ConfidenceResult(
            location=None,
            event="unknown",
            confidence_score=0,
            reliability=classify_reliability(0),
            alert=predict_alert(0),
            explanation="No usable data was provided, so no confidence assessment could be made.",
            contributing_sources=[],
            conflicting_sources=[],
        )

    score, contributing, conflicting = score_event(observations)
    reliability = classify_reliability(score)
    alert = predict_alert(score)

    # Report on the signal most observations agree on.
    signal_counts: Dict[str, int] = {}
    for obs in observations:
        signal_counts[obs.signal] = signal_counts.get(obs.signal, 0) + 1
    event = max(signal_counts, key=signal_counts.get)

    explanation = generate_explanation(event, score, reliability, contributing, conflicting)

    return ConfidenceResult(
        location=_pick_representative_location(observations),
        event=event,
        confidence_score=score,
        reliability=reliability,
        alert=alert,
        explanation=explanation,
        contributing_sources=contributing,
        conflicting_sources=conflicting,
    )


def run_multi_event_pipeline(
    raw_inputs: List[Dict[str, Any]],
    radius_km: float = 5.0,
    window_minutes: float = 120,
) -> List[ConfidenceResult]:
    """
    Use this instead of run_confidence_pipeline when a single incoming
    batch may contain reports about SEVERAL different, unrelated
    events/locations at once (e.g. a flood in one district and a
    wildfire in another, all reported in the same time window) — the
    realistic case for a live monitoring feed rather than a
    single-scenario demo.

    It clusters raw_inputs by location + time proximity first, then
    runs the full single-event pipeline independently on each cluster,
    so events don't get blended into one confusing score.

    Args:
        raw_inputs: a mixed batch of raw observation dicts, potentially
            spanning multiple real-world events.
        radius_km: max distance between two reports to be treated as the same event.
        window_minutes: max time gap between two reports to be treated as the same event.

    Returns:
        One ConfidenceResult per detected event cluster.
    """
    clusters = cluster_observations(raw_inputs, radius_km=radius_km, window_minutes=window_minutes)
    return [run_confidence_pipeline(cluster) for cluster in clusters]
