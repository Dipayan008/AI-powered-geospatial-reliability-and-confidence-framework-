## Quick start

**AI engine only (no server, quick sanity check):**
```bash
pip install -r requirements.txt
python test_demo.py
```

**Full backend (DB + API + real AI scoring):**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

Then in another terminal, ingest a source and generate an insight:
```bash
curl -X POST http://127.0.0.1:8001/sources \
     -H "Content-Type: application/json" \
     -d '{"name":"Test","source_type":"citizen_report","raw_content":"Heavy flooding reported","latitude":22.57,"longitude":88.36}'

curl -X POST "http://127.0.0.1:8001/insights/generate?title=Test&summary=Test%20run" \
     -H "Content-Type: application/json" \
     -d '[1]'
```

**Frontend:**
```bash
npm install
npm run dev
```

## Running tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Covers: multi-source corroboration, conflicting-source detection, weak-single-source handling, empty-input safety, and multi-event clustering.