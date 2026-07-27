"""
weights_config.py
------------------
Every scoring number the engine uses, in one place, with a written
rationale for each — and a way to override them without touching code.

Why this file exists: a judge WILL ask "why does satellite get 35 base
points and not 40?" The honest answer for a hackathon is "these are
sensible defaults grounded in how much independent, verifiable signal
each source type typically carries — and they're deliberately exposed
as config, not hardcoded truth, because real deployments in different
regions/disaster types would want to recalibrate them." That's what
this file makes possible.

To override at runtime (e.g. for a specific region or disaster type)
without editing code, set the environment variable
GEOTRUST_WEIGHTS_JSON to a JSON object matching the shape of
DEFAULT_TRUST_WEIGHTS / DEFAULT_BASE_POINTS, e.g.:

    export GEOTRUST_WEIGHTS_JSON='{"trust_weights": {"user_report": 0.3}}'
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict


# --------------------------------------------------------------------------
# Source trust weights (0-1): how much we trust a source TYPE in general,
# independent of any single report's own stated confidence.
#
# Rationale:
#   satellite (1.0)     — direct sensor imagery, no human relay step,
#                         hardest to fake or mis-transcribe. Main
#                         weakness is cloud cover / revisit-time gaps,
#                         not reliability of what it does capture.
#   weather (0.9)       — official meteorological APIs (aggregated
#                         station + model data), high institutional
#                         accountability, near-real-time.
#   news (0.7)          — professionally fact-checked before
#                         publication, but is itself a secondhand
#                         relay of other sources and lags real-time.
#   osm (0.6)           — community-maintained map data; accurate for
#                         static geography, weaker for real-time event
#                         state since it's not built for that.
#   user_report (0.5)   — most valuable for ground-truth immediacy
#                         (someone standing in the flood right now),
#                         but least verifiable and most exposed to
#                         error/exaggeration/malice — hence also
#                         capped (see MULTI_USER_REPORT_CAP below) so
#                         no volume of crowd reports alone can
#                         outweigh one corroborating institutional source.
# --------------------------------------------------------------------------
DEFAULT_TRUST_WEIGHTS: Dict[str, float] = {
    "satellite": 1.0,
    "weather": 0.9,
    "osm": 0.6,
    "user_report": 0.5,
    "news": 0.7,
}

# --------------------------------------------------------------------------
# Base points awarded per confirming source type before trust-weighting.
# Deliberately scaled so that satellite + weather alone (35*1.0 + 25*0.9
# = 57.5) plus the independent-agreement bonus already clears the
# "Medium" reliability threshold (50) — reflecting that two independent
# institutional sources agreeing should already count for a lot, while
# still leaving room for user reports / news to push it to High or
# Very High.
# --------------------------------------------------------------------------
DEFAULT_BASE_POINTS: Dict[str, float] = {
    "satellite": 35,
    "weather": 25,
    "osm": 10,
    "user_report": 15,
    "news": 20,
}

# Bonus for 2+ independent (non-user-report) source TYPES agreeing —
# models the idea that independent corroboration is worth more than
# the sum of its parts.
DEFAULT_AGREEMENT_BONUS = 10

# Points subtracted per conflicting observation, weighted by that
# source's trust. Set close to a full source's worth of points so a
# single credible denial meaningfully shakes confidence rather than
# being a rounding error.
DEFAULT_CONFLICT_PENALTY = 20

# Ceiling on how many total points ALL user reports combined can
# contribute — this is the mechanism that stops "50 people tweeted
# about it" from mathematically outscoring one satellite pass.
DEFAULT_MULTI_USER_REPORT_CAP = 20

# Reliability score thresholds.
DEFAULT_RELIABILITY_THRESHOLDS: Dict[str, int] = {
    "very_high": 90,
    "high": 75,
    "medium": 50,
}

# Alert level score thresholds.
DEFAULT_ALERT_THRESHOLDS: Dict[str, int] = {
    "high": 85,   # score > this -> High Alert
    "medium": 60,  # score >= this -> Medium Alert, else Low Alert
}


def _load_overrides() -> Dict[str, Any]:
    """Read GEOTRUST_WEIGHTS_JSON from the environment, if set."""
    raw = os.environ.get("GEOTRUST_WEIGHTS_JSON")
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Bad config shouldn't crash the whole engine — just ignore it.
        return {}


def get_trust_weights() -> Dict[str, float]:
    overrides = _load_overrides().get("trust_weights", {})
    return {**DEFAULT_TRUST_WEIGHTS, **overrides}


def get_base_points() -> Dict[str, float]:
    overrides = _load_overrides().get("base_points", {})
    return {**DEFAULT_BASE_POINTS, **overrides}


def get_scalar(name: str, default: float) -> float:
    """Fetch a single scalar override (agreement bonus, conflict penalty, etc.)."""
    overrides = _load_overrides()
    return overrides.get(name, default)
