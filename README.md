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