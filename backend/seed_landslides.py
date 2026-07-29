import pandas as pd
import requests
import time

BASE_URL = "https://ai-powered-geospatial-reliability-and-1mxp.onrender.com"

df = pd.read_csv("landslides_india_clean.csv")
df = df.head(1)  # start with 10 as a test batch

for _, row in df.iterrows():
    source_payload = {
        "name": f"Landslide - {row['title']}",
        "source_type": "landslide",
        "raw_content": (
            f"{row['landslide_category']} landslide at {row['location_description']}, {row['region']}. "
            f"Triggered by {row['trigger']}. Size: {row['size']}. "
            f"Fatalities: {row['fatality_count']}. Date: {row['event_date']}. "
            f"Source: {row['source_name']}."
        ),
        "latitude": row['latitude'],
        "longitude": row['longitude'],
    }

    res = requests.post(f"{BASE_URL}/sources", json=source_payload)
    print("Source created:", res.status_code, res.json())

    if res.status_code == 200:
        source_id = res.json()["id"]
        title = f"Landslide near {row['region']}"
        summary = f"{row['landslide_category']} triggered by {row['trigger']}, size {row['size']}."

        insight_res = requests.post(
            f"{BASE_URL}/insights/generate",
            params={"title": title, "summary": summary},
            json=[source_id],
        )
        print("Insight generated:", insight_res.status_code, insight_res.json())

    time.sleep(1)