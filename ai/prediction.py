"""
prediction.py
--------------
Maps a confidence score to an alert level for the dashboard's
notification system.
"""

from __future__ import annotations

from .utils import AlertLevel
from .weights_config import DEFAULT_ALERT_THRESHOLDS, get_scalar


def predict_alert(score: int) -> AlertLevel:
    """
    Thresholds are documented and overridable in weights_config.py
    (DEFAULT_ALERT_THRESHOLDS).

        >85     High Alert
        60-85   Medium Alert
        <60     Low Alert
    """
    high = get_scalar("alert_high", DEFAULT_ALERT_THRESHOLDS["high"])
    medium = get_scalar("alert_medium", DEFAULT_ALERT_THRESHOLDS["medium"])

    if score > high:
        return AlertLevel.HIGH
    if score >= medium:
        return AlertLevel.MEDIUM
    return AlertLevel.LOW
