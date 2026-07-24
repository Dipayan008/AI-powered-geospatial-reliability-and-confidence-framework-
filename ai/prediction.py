"""
prediction.py
--------------
Maps a confidence score to an alert level for the dashboard's
notification system.
"""

from __future__ import annotations

from .utils import AlertLevel


def predict_alert(score: int) -> AlertLevel:
    """
        >85     High Alert
        60-85   Medium Alert
        <60     Low Alert
    """
    if score > 85:
        return AlertLevel.HIGH
    if score >= 60:
        return AlertLevel.MEDIUM
    return AlertLevel.LOW
