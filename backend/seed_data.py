import pandas as pd
import requests
import time

BASE_URL = "https://ai-powered-geospatial-reliability-and-1mxp.onrender.com"

df = pd.read_csv("earthquakes_clean.csv")
# df = df.head(5)  # test with 5 rows first

for _, row in df.iterrows():
    source_payload = {
        "name": f"Earthquake M{row['magnitude']} - {row['region']}",
        "source_type": "earthquake",
        "raw_content": (
            f"Magnitude {row['magnitude']} earthquake at {row['location']}, "
            f"depth {row['depth_km']}km, occurred {row['origin_time_utc']}. "
            f"Status: {row['review_status']}. {row['felt_report']}."
        ),
        "latitude": row['latitude'],
        "longitude": row['longitude'],
    }

    res = requests.post(f"{BASE_URL}/sources", json=source_payload)
    print("Source created:", res.status_code, res.json())

    if res.status_code == 200:
        source_id = res.json()["id"]
        title = f"Earthquake M{row['magnitude']} near {row['region']}"
        summary = f"Detected at {row['location']}, depth {row['depth_km']}km."

        insight_res = requests.post(
            f"{BASE_URL}/insights/generate",
            params={"title": title, "summary": summary},
            json=[source_id],  # body is a list of source_ids
        )
        print("Insight generated:", insight_res.status_code, insight_res.json())

    time.sleep(1)