"""
Automated tests for the AI confidence engine (ai/model.py).
Run with: pytest tests/test_confidence_engine.py -v

These assert on BEHAVIOR (direction/category of the result) rather than
exact scores, so the tests stay meaningful even if scoring weights are
tuned later, but still catch real regressions (e.g. import errors,
broken pipelines, or corroboration logic silently breaking).
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.model import run_confidence_pipeline, run_multi_event_pipeline


def test_strong_agreement_gives_high_confidence():
    """Multiple independent sources agreeing should yield High/Very High reliability."""
    raw_inputs = [
        {"source": "satellite", "signal": "Flood Detected", "location": [22.5726, 88.3639], "confidence": 0.92},
        {"source": "weather", "signal": "Heavy Rain", "location": [22.5730, 88.3641], "confidence": 0.88},
        {"source": "user_report", "signal": "Road Under Water", "location": [22.5720, 88.3635]},
        {"source": "user_report", "signal": "Road Under Water", "location": [22.5722, 88.3636]},
        {"source": "news", "signal": "Flood Confirmed", "location": [22.5725, 88.3640], "confidence": 0.8},
    ]
    result = run_confidence_pipeline(raw_inputs).to_dict()

    assert result["confidence_score"] >= 70
    assert result["reliability"] in ("High", "Very High")
    assert len(result["contributing_sources"]) >= 3
    assert len(result["conflicting_sources"]) == 0


def test_conflicting_sources_lower_confidence():
    """Sources that disagree should pull the score down and be flagged as conflicting."""
    raw_inputs = [
        {"source": "satellite", "signal": "Flood Detected", "location": [22.57, 88.36], "confidence": 0.7},
        {"source": "weather", "signal": "No Rain", "location": [22.571, 88.361], "confidence": 0.6},
        {"source": "user_report", "signal": "All Clear", "location": [22.572, 88.362]},
    ]
    result = run_confidence_pipeline(raw_inputs).to_dict()

    assert result["confidence_score"] < 50
    assert result["reliability"] == "Low"
    assert len(result["conflicting_sources"]) >= 1


def test_single_weak_report_gives_low_confidence():
    """A single uncorroborated user report should not produce high confidence."""
    raw_inputs = [
        {"source": "user_report", "signal": "Possible Flooding", "location": [22.6, 88.4]},
    ]
    result = run_confidence_pipeline(raw_inputs).to_dict()

    assert result["confidence_score"] < 30
    assert result["reliability"] == "Low"
    assert result["contributing_sources"] == ["user_report"]


def test_empty_input_does_not_crash():
    """No usable data should return a safe zero-confidence result, not raise an exception."""
    result = run_confidence_pipeline([]).to_dict()

    assert result["confidence_score"] == 0
    assert result["event"] == "unknown"


def test_multi_event_pipeline_splits_unrelated_events():
    """A mixed batch spanning two distant, unrelated events must split into 2 clusters,
    not get blended into one confused score."""
    mixed_batch = [
        # Kolkata flood cluster
        {"source": "satellite", "signal": "Flood Detected", "location": [22.5726, 88.3639], "confidence": 0.9},
        {"source": "weather", "signal": "Heavy Rain", "location": [22.5730, 88.3641], "confidence": 0.85},
        {"source": "user_report", "signal": "Road Under Water", "location": [22.5720, 88.3635]},
        # Wildfire cluster, ~300km away
        {"source": "satellite", "signal": "Wildfire Detected", "location": [23.2599, 87.8550], "confidence": 0.8},
        {"source": "user_report", "signal": "Smoke Visible", "location": [23.2605, 87.8555]},
    ]
    results = run_multi_event_pipeline(mixed_batch)

    assert len(results) == 2
    events = {r.to_dict()["event"] for r in results}
    assert "flood_detected" in events
    assert "wildfire_detected" in events


def test_unknown_source_type_is_skipped_not_crashed():
    """An observation with an invalid/unknown source type should be dropped safely."""
    raw_inputs = [
        {"source": "not_a_real_source", "signal": "Flood Detected", "location": [22.57, 88.36]},
        {"source": "satellite", "signal": "Flood Detected", "location": [22.57, 88.36], "confidence": 0.9},
    ]
    result = run_confidence_pipeline(raw_inputs).to_dict()

    # Should still process the one valid observation without raising
    assert result["contributing_sources"] == ["satellite"]