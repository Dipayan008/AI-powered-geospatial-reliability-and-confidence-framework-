"""
preprocessing.py
-----------------
Takes raw, messy input from multiple sources (satellite, weather, OSM,
user reports, news) and turns it into a clean list of SourceObservation
objects that the rest of the pipeline can work with.

Responsibilities:
  1. Normalize each source's raw payload into a common schema.
  2. Drop malformed / incomplete entries instead of crashing.
  3. Deduplicate near-identical reports (e.g. 5 users reporting the
     same flood at the same spot within a few minutes).
"""

from __future__ import annotations

from typing import Any, Dict, List

from .utils import SourceObservation, SourceType, infer_polarity, same_location

# Default trust weights per source type. These can be tuned later, or
# replaced with a learned per-source reliability score once you have
# historical accuracy data for each feed.
DEFAULT_TRUST_WEIGHTS: Dict[str, float] = {
    SourceType.SATELLITE.value: 1.0,
    SourceType.WEATHER.value: 0.9,
    SourceType.OSM.value: 0.6,
    SourceType.USER_REPORT.value: 0.5,
    SourceType.NEWS.value: 0.7,
}


def _normalize_one(raw: Dict[str, Any], trust_weights: Dict[str, float]) -> SourceObservation | None:
    """Convert one raw dict into a SourceObservation, or None if invalid."""
    source_raw = raw.get("source")
    signal = raw.get("signal") or raw.get("event")

    if not source_raw or not signal:
        return None  # can't use an observation with no source or no signal

    try:
        source = SourceType(source_raw)
    except ValueError:
        # Unknown source type — skip rather than guess.
        return None

    location = raw.get("location")
    if location and (not isinstance(location, (list, tuple)) or len(location) != 2):
        location = None  # malformed coordinates are treated as "unknown"

    normalized_signal = str(signal).strip().lower().replace(" ", "_")

    return SourceObservation(
        source=source,
        signal=normalized_signal,
        location=list(location) if location else None,
        timestamp=raw.get("timestamp"),
        raw_confidence=raw.get("confidence"),
        trust_weight=trust_weights.get(source.value, 0.5),
        polarity=infer_polarity(normalized_signal),
        metadata={k: v for k, v in raw.items()
                  if k not in {"source", "signal", "event", "location", "timestamp", "confidence"}},
    )


def _deduplicate(observations: List[SourceObservation],
                  radius_km: float = 2.0) -> List[SourceObservation]:
    """
    Collapse multiple observations that are the same source type,
    same signal, and same location into one (keeping the highest
    raw_confidence if present). This stops 10 identical user reports
    from unfairly dominating the score the way 10 independent sources
    would.
    """
    kept: List[SourceObservation] = []
    for obs in observations:
        duplicate_of = None
        for existing in kept:
            if (existing.source == obs.source
                    and existing.signal == obs.signal
                    and same_location(existing.location, obs.location, radius_km)):
                duplicate_of = existing
                break
        if duplicate_of is None:
            kept.append(obs)
        else:
            # Keep the more confident / more detailed of the two duplicates.
            if (obs.raw_confidence or 0) > (duplicate_of.raw_confidence or 0):
                kept.remove(duplicate_of)
                kept.append(obs)
    return kept


def preprocess(raw_inputs: List[Dict[str, Any]],
               trust_weights: Dict[str, float] | None = None) -> List[SourceObservation]:
    """
    Main entry point.

    Args:
        raw_inputs: list of raw dicts, one per observation, e.g.
            [{"source": "satellite", "signal": "Flood Detected",
              "location": [22.57, 88.36], "timestamp": "2026-07-25T01:00:00Z",
              "confidence": 0.92}, ...]
        trust_weights: optional override of DEFAULT_TRUST_WEIGHTS.

    Returns:
        A cleaned, deduplicated list of SourceObservation objects.
    """
    weights = trust_weights or DEFAULT_TRUST_WEIGHTS

    normalized = [_normalize_one(r, weights) for r in raw_inputs]
    valid = [obs for obs in normalized if obs is not None]

    return _deduplicate(valid)
