# GeoTrust AI — Confidence Engine (PS07, AI/ML module)

This is the AI/ML piece of GeoTrust AI: it takes raw observations from
multiple space/geospatial sources (satellite, weather, OSM, user
reports, news), decides how much they agree or conflict, and returns a
0–100 confidence score with an explainable-AI justification and an
alert level.

## Folder structure

```
ai/
  utils.py             shared types (SourceObservation, ConfidenceResult, enums)
  preprocessing.py      cleans + normalizes + deduplicates raw input
  confidence_engine.py  core scoring logic (confirm vs deny, agreement/conflict)
  reliability.py        score -> Low/Medium/High/Very High
  explanation.py        Gemini-based explanation, with safe offline fallback
  prediction.py         score -> alert level
  model.py              orchestrator — the only file the backend needs to import
main.py                 FastAPI wrapper exposing POST /analyze
test_demo.py            run 3 example scenarios without starting the server
sample_data.json        example payload for curl / Postman
requirements.txt
```

## Quick start

```bash
pip install -r requirements.txt

# Try it without any server:
python test_demo.py

# Or run the API:
uvicorn main:app --reload
# then in another terminal:
curl -X POST http://127.0.0.1:8000/analyze \
     -H "Content-Type: application/json" \
     -d @sample_data.json
```

## How scoring works (the part judges will ask about)

1. **Preprocessing** normalizes every source into the same shape and
   drops/merges duplicates (e.g. 5 identical user reports of the same
   flood within 2 km collapse into 1).
2. Each observation is tagged **confirm** or **deny** based on its
   signal wording (`flood_detected` = confirm, `no_rain` = deny) — this
   lets sources that phrase things differently (a satellite says
   "flood_detected", a citizen says "road_under_water") still be
   recognized as agreeing.
3. The **confidence engine** sums weighted points for the side
   (confirm/deny) backed by more independent source types, gives a
   bonus for 2+ independent sources agreeing, and subtracts a penalty
   for every source on the losing side.
4. **Reliability** buckets the 0–100 score into Low / Medium / High /
   Very High.
5. **Explanation** asks Gemini for a 1–2 sentence plain-English reason
   ("confidence is 81% because satellite, weather, and news reports
   all agree"); if there's no API key or the call fails, it falls back
   to a template that says the same thing — so the demo never breaks
   on a live API call.
6. **Alert level** maps the score to Low / Medium / High Alert for the
   dashboard's notification panel.

## Wiring into the rest of the app

Backend (Member 2) only needs:

```python
from ai.model import run_confidence_pipeline

result = run_confidence_pipeline(raw_observations)  # list of dicts
payload = result.to_dict()                          # JSON-ready
```

Or just call the already-built `/analyze` endpoint from `main.py`
directly from the Next.js frontend.

## To set up Gemini explanations (optional but nice for the demo)

```bash
export GOOGLE_API_KEY="your-key-here"
```

Without this set, explanations still work — they're just generated
from a template instead of Gemini's phrasing.

## Tuning knobs

All the "why did it score this way" numbers live in
`confidence_engine.py` (`BASE_POINTS`, `AGREEMENT_BONUS`,
`CONFLICT_PENALTY`) and `reliability.py` / `prediction.py`
(the score thresholds) — tune these live during Day 3 based on
what feels right for your demo scenarios.
