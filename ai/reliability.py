"""
reliability.py
---------------
Turns a raw 0-100 confidence score into a human-friendly reliability
category. Kept as its own module so the thresholds are easy to find
and tune independently of the scoring math.
"""

from __future__ import annotations

from .utils import ReliabilityLevel


def classify_reliability(score: int) -> ReliabilityLevel:
    """
    Score -> Reliability band.

        90-100  Very High
        75-89   High
        50-74   Medium
        <50     Low
    """
    if score >= 90:
        return ReliabilityLevel.VERY_HIGH
    if score >= 75:
        return ReliabilityLevel.HIGH
    if score >= 50:
        return ReliabilityLevel.MEDIUM
    return ReliabilityLevel.LOW
