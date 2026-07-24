"""
utils.py
--------
Shared type definitions, enums, and small helper functions used across
the GeoTrust AI confidence engine (PS07).

Keeping these in one place means every other module (preprocessing,
confidence_engine, reliability, explanation, prediction) speaks the
same data "language" and can be unit-tested independently.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


# --------------------------------------------------------------------------
# Enums
# --------------------------------------------------------------------------

class SourceType(str, Enum):
    SATELLITE = "satellite"
    WEATHER = "weather"
    OSM = "osm"
    USER_REPORT = "user_report"
    NEWS = "news"


class ReliabilityLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    VERY_HIGH = "Very High"


class AlertLevel(str, Enum):
    LOW = "Low Alert"
    MEDIUM = "Medium Alert"
    HIGH = "High Alert"


# --------------------------------------------------------------------------
# Core data structures
# --------------------------------------------------------------------------

@dataclass
class SourceObservation:
    """
    A single normalized observation coming from one data source.

    Example (raw, before normalization):
        {"source": "satellite", "signal": "flood_detected",
         "location": [22.57, 88.36], "timestamp": "...", "trust": 0.9}
    """
    source: SourceType
    signal: str                      # normalized event label, e.g. "flood_detected"
    location: Optional[List[float]] = None   # [lat, lon]
    timestamp: Optional[str] = None
    raw_confidence: Optional[float] = None   # 0-1, if the source itself reports one
    trust_weight: float = 1.0                # how much we trust this source type
    polarity: str = "confirm"                # "confirm" (event is happening) or "deny" (event is not)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfidenceResult:
    """Final output object returned to the backend / frontend."""
    location: Optional[List[float]]
    event: str
    confidence_score: int                    # 0-100
    reliability: ReliabilityLevel
    alert: AlertLevel
    explanation: str
    contributing_sources: List[str]
    conflicting_sources: List[str]
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "location": self.location,
            "event": self.event,
            "confidence_score": self.confidence_score,
            "reliability": self.reliability.value,
            "alert": self.alert.value,
            "explanation": self.explanation,
            "contributing_sources": self.contributing_sources,
            "conflicting_sources": self.conflicting_sources,
            "generated_at": self.generated_at,
        }


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    """Keep a score inside a valid range."""
    return max(low, min(high, value))


def haversine_km(p1: List[float], p2: List[float]) -> float:
    """
    Great-circle distance between two [lat, lon] points, in km.
    Used to decide whether two reports are "about the same place".
    """
    from math import radians, sin, cos, sqrt, atan2

    lat1, lon1 = radians(p1[0]), radians(p1[1])
    lat2, lon2 = radians(p2[0]), radians(p2[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    earth_radius_km = 6371.0
    return earth_radius_km * c


def same_location(p1: Optional[List[float]], p2: Optional[List[float]],
                   radius_km: float = 5.0) -> bool:
    """Whether two points are close enough to be considered the same event site."""
    if not p1 or not p2:
        return False
    return haversine_km(p1, p2) <= radius_km


# Keywords that flip a signal from "confirming" the event to "denying" it.
# This is intentionally simple (keyword-based) so it's transparent and
# easy to extend — add more negation words here as you encounter them,
# or replace this with a small classifier later.
_NEGATION_KEYWORDS = (
    "no_", "not_", "clear", "false", "normal", "safe", "resolved", "absent",
)


def infer_polarity(signal: str) -> str:
    """
    Decide whether a normalized signal string confirms an event
    ("flood_detected", "heavy_rain", "road_under_water") or denies /
    contradicts it ("no_rain", "all_clear", "false_alarm").

    Different sources rarely use identical wording for the same event
    (a satellite says "flood_detected", a user says "road_under_water"),
    so the engine groups by polarity rather than exact signal text.
    """
    lowered = signal.lower()
    if any(keyword in lowered for keyword in _NEGATION_KEYWORDS):
        return "deny"
    return "confirm"
