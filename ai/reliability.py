"""
reliability.py
---------------
Turns a raw 0-100 confidence score into a human-friendly reliability
category. Kept as its own module so the thresholds are easy to find
and tune independently of the scoring math.
"""

from __future__ import annotations

from .utils import ReliabilityLevel
from .weights_config import DEFAULT_RELIABILITY_THRESHOLDS, get_scalar


def classify_reliability(score: int) -> ReliabilityLevel:
    """
    Score -> Reliability band. Thresholds are documented and
    overridable in weights_config.py (DEFAULT_RELIABILITY_THRESHOLDS).

        90-100  Very High
        75-89   High
        50-74   Medium
        <50     Low
    """
    very_high = get_scalar("reliability_very_high", DEFAULT_RELIABILITY_THRESHOLDS["very_high"])
    high = get_scalar("reliability_high", DEFAULT_RELIABILITY_THRESHOLDS["high"])
    medium = get_scalar("reliability_medium", DEFAULT_RELIABILITY_THRESHOLDS["medium"])

    if score >= very_high:
        return ReliabilityLevel.VERY_HIGH
    if score >= high:
        return ReliabilityLevel.HIGH
    if score >= medium:
        return ReliabilityLevel.MEDIUM
    return ReliabilityLevel.LOW
