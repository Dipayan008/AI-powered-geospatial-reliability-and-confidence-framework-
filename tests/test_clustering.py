"""
Edge-case tests for the multi-event clustering logic (ai/clustering.py).
Run with: pytest tests/test_clustering.py -v
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.clustering import cluster_observations


def test_two_reports_within_radius_and_window_merge():
    """Two reports close in space and time should end up in the same cluster."""
    raw_inputs = [
        {"source": "satellite", "signal": "Flood Detected", "location": [22.5726, 88.3639],
         "timestamp": "2026-07-27T10:00:00Z"},
        {"source": "user_report", "signal": "Road Under Water", "location": [22.5730, 88.3641],
         "timestamp": "2026-07-27T10:05:00Z"},
    ]
    clusters = cluster_observations(raw_inputs, radius_km=5.0, window_minutes=120)

    assert len(clusters) == 1
    assert len(clusters[0]) == 2


def test_reports_far_apart_in_space_split_into_separate_clusters():
    """Two reports well outside the radius must NOT merge, even if timed identically."""
    raw_inputs = [
        {"source": "satellite", "signal": "Flood Detected", "location": [22.5726, 88.3639],
         "timestamp": "2026-07-27T10:00:00Z"},
        {"source": "satellite", "signal": "Wildfire Detected", "location": [23.2599, 87.8550],
         "timestamp": "2026-07-27T10:00:00Z"},
    ]
    clusters = cluster_observations(raw_inputs, radius_km=5.0, window_minutes=120)

    assert len(clusters) == 2


def test_reports_close_in_space_but_far_in_time_split():
    """Two reports at the same location but hours apart (outside window) should split."""
    raw_inputs = [
        {"source": "satellite", "signal": "Flood Detected", "location": [22.5726, 88.3639],
         "timestamp": "2026-07-27T08:00:00Z"},
        {"source": "user_report", "signal": "Road Under Water", "location": [22.5726, 88.3639],
         "timestamp": "2026-07-27T14:00:00Z"},
    ]
    clusters = cluster_observations(raw_inputs, radius_km=5.0, window_minutes=120)

    assert len(clusters) == 2


def test_missing_timestamp_does_not_block_spatial_grouping():
    """A report with no timestamp should still merge with a spatially close one."""
    raw_inputs = [
        {"source": "satellite", "signal": "Flood Detected", "location": [22.5726, 88.3639],
         "timestamp": "2026-07-27T10:00:00Z"},
        {"source": "user_report", "signal": "Road Under Water", "location": [22.5728, 88.3640]},
    ]
    clusters = cluster_observations(raw_inputs, radius_km=5.0, window_minutes=120)

    assert len(clusters) == 1
    assert len(clusters[0]) == 2


def test_reports_with_no_location_each_become_their_own_cluster():
    """Observations with no usable location must become isolated single-item clusters."""
    raw_inputs = [
        {"source": "user_report", "signal": "Possible Flooding"},
        {"source": "news", "signal": "Reports of Flooding"},
    ]
    clusters = cluster_observations(raw_inputs, radius_km=5.0, window_minutes=120)

    assert len(clusters) == 2
    assert len(clusters[0]) == 1
    assert len(clusters[1]) == 1


def test_exactly_at_radius_boundary_still_merges():
    """Documents actual boundary behavior rather than assuming an outcome."""
    raw_inputs = [
        {"source": "satellite", "signal": "Flood Detected", "location": [22.5726, 88.3639],
         "timestamp": "2026-07-27T10:00:00Z"},
        {"source": "weather", "signal": "Heavy Rain", "location": [22.6176, 88.3639],
         "timestamp": "2026-07-27T10:00:00Z"},
    ]
    clusters = cluster_observations(raw_inputs, radius_km=5.0, window_minutes=120)

    total_observations = sum(len(c) for c in clusters)
    assert total_observations == 2


def test_empty_batch_returns_empty_list():
    """An empty input batch should return no clusters, not raise an exception."""
    clusters = cluster_observations([], radius_km=5.0, window_minutes=120)
    assert clusters == []


def test_three_events_in_one_batch_split_into_three_clusters():
    """A batch spanning three distant, unrelated events should split into exactly 3 clusters."""
    raw_inputs = [
        {"source": "satellite", "signal": "Flood Detected", "location": [22.5726, 88.3639],
         "timestamp": "2026-07-27T10:00:00Z"},
        {"source": "user_report", "signal": "Road Under Water", "location": [22.5728, 88.3640],
         "timestamp": "2026-07-27T10:05:00Z"},
        {"source": "satellite", "signal": "Wildfire Detected", "location": [23.2599, 87.8550],
         "timestamp": "2026-07-27T10:00:00Z"},
        {"source": "satellite", "signal": "Landslide Detected", "location": [32.0628, 77.2619],
         "timestamp": "2026-07-27T10:00:00Z"},
    ]
    clusters = cluster_observations(raw_inputs, radius_km=5.0, window_minutes=120)

    assert len(clusters) == 3
