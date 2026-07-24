"""
test_demo.py
------------
Run this directly to sanity-check the confidence engine without
starting the FastAPI server:

    python test_demo.py

It runs three scenarios: strong agreement (should be Very High /
High Alert), conflicting sources (should be lower / Medium), and
a single weak report (should be Low).
"""

import json

from ai.model import run_confidence_pipeline

SCENARIOS = {
    "Strong agreement (flood)": [
        {"source": "satellite", "signal": "Flood Detected", "location": [22.5726, 88.3639], "confidence": 0.92},
        {"source": "weather", "signal": "Heavy Rain", "location": [22.5730, 88.3641], "confidence": 0.88},
        {"source": "user_report", "signal": "Road Under Water", "location": [22.5720, 88.3635]},
        {"source": "user_report", "signal": "Road Under Water", "location": [22.5722, 88.3636]},
        {"source": "news", "signal": "Flood Confirmed", "location": [22.5725, 88.3640], "confidence": 0.8},
    ],
    "Conflicting sources": [
        {"source": "satellite", "signal": "Flood Detected", "location": [22.57, 88.36], "confidence": 0.7},
        {"source": "weather", "signal": "No Rain", "location": [22.571, 88.361], "confidence": 0.6},
        {"source": "user_report", "signal": "All Clear", "location": [22.572, 88.362]},
    ],
    "Single weak report": [
        {"source": "user_report", "signal": "Possible Flooding", "location": [22.6, 88.4]},
    ],
}

if __name__ == "__main__":
    for name, raw_inputs in SCENARIOS.items():
        result = run_confidence_pipeline(raw_inputs)
        print(f"\n=== {name} ===")
        print(json.dumps(result.to_dict(), indent=2))
