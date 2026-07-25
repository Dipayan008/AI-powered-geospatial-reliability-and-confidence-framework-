"""
confidence_engine.py
---------------------
The heart of GeoTrust AI. Takes a cleaned list of SourceObservations
(all believed to be about the same event/location) and produces a
0-100 confidence score, plus which sources agreed and which
conflicted.

Design: a transparent, tunable rule-based scorer rather than a black
box model. This is deliberate for a hackathon — judges can see exactly
*why* a score came out the way it did, and explainability is one of
your stated success metrics. It can be swapped for a trained model
later (see model.py) without changing the interface.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from .utils import SourceObservation, SourceType, clamp
from .weights_config import get_base_points, get_scalar

# Base points awarded when a source type confirms the event, scaled by
# that source's trust weight. Full rationale for these numbers lives in
# weights_config.py — kept as a module-level name here for backward
# compatibility.
BASE_POINTS: Dict[str, float] = get_base_points()

# Bonus for agreement between two or more independent, high-trust sources.
AGREEMENT_BONUS = get_scalar("agreement_bonus", 10)
# Penalty applied per conflicting observation (a source reporting "no
# event" or a contradicting signal for the same location).
CONFLICT_PENALTY = get_scalar("conflict_penalty", 20)
MULTI_USER_REPORT_CAP = get_scalar("multi_user_report_cap", 20)  # avoid many low-trust reports dominating the score


def _group_by_polarity(observations: List[SourceObservation]) -> Dict[str, List[SourceObservation]]:
    """
    Group observations into "confirm" (event is happening, e.g.
    flood_detected / heavy_rain / road_under_water) vs "deny" (event is
    not happening, e.g. no_rain / all_clear). Different sources rarely
    phrase the same event identically, so grouping by polarity — not
    exact signal text — is what lets a satellite's "flood_detected" and
    a user's "road_under_water" agree with each other.
    """
    groups: Dict[str, List[SourceObservation]] = {"confirm": [], "deny": []}
    for obs in observations:
        groups[obs.polarity].append(obs)
    return groups


def score_event(observations: List[SourceObservation]) -> Tuple[int, List[str], List[str]]:
    """
    Compute a confidence score for one location/event cluster.

    Args:
        observations: SourceObservations already filtered down to a
            single place and time window (e.g. all reports about the
            same flood).

    Returns:
        (confidence_score, contributing_sources, conflicting_sources)
    """
    if not observations:
        return 0, [], []

    polarity_groups = _group_by_polarity(observations)

    # Majority polarity = whichever side has more distinct, independent
    # (non-user-report) source types backing it. Ties default to "confirm"
    # since that's the actionable case (better to flag a possible event
    # than silently drop it).
    def independent_type_count(group: List[SourceObservation]) -> int:
        return len({o.source for o in group if o.source != SourceType.USER_REPORT})

    majority_polarity = "confirm"
    if independent_type_count(polarity_groups["deny"]) > independent_type_count(polarity_groups["confirm"]):
        majority_polarity = "deny"

    supporting = polarity_groups[majority_polarity]
    opposing = polarity_groups["deny" if majority_polarity == "confirm" else "confirm"]

    score = 0.0
    contributing_sources: List[str] = []
    seen_source_types = set()
    user_report_points = 0.0

    for obs in supporting:
        base = BASE_POINTS.get(obs.source.value, 10)
        weighted = base * obs.trust_weight
        # If the source itself gave a raw confidence, blend it in
        # instead of trusting a flat base value.
        if obs.raw_confidence is not None:
            weighted *= clamp(obs.raw_confidence, 0, 1)

        if obs.source == SourceType.USER_REPORT:
            # Cap so many crowd reports can't outweigh one satellite pass.
            user_report_points = min(user_report_points + weighted, MULTI_USER_REPORT_CAP)
        else:
            score += weighted
            if obs.source.value not in seen_source_types:
                contributing_sources.append(obs.source.value)
                seen_source_types.add(obs.source.value)

    score += user_report_points
    if supporting and any(o.source == SourceType.USER_REPORT for o in supporting):
        contributing_sources.append(SourceType.USER_REPORT.value)

    # Reward independent agreement: 2+ distinct high-trust source TYPES
    # backing the same conclusion is stronger evidence than any one alone.
    independent_types = {o.source for o in supporting if o.source != SourceType.USER_REPORT}
    if len(independent_types) >= 2:
        score += AGREEMENT_BONUS

    # Penalize sources that disagree with the majority conclusion.
    conflicting_sources: List[str] = []
    for obs in opposing:
        score -= CONFLICT_PENALTY * obs.trust_weight
        if obs.source.value not in conflicting_sources:
            conflicting_sources.append(obs.source.value)

    return int(round(clamp(score))), contributing_sources, conflicting_sources
