"""
Bulk-loads ALL of India's data (not filtered to one state) directly into
the database. Uses direct DB inserts instead of calling the API per row,
because the weather file alone has 91,000+ rows — that would take hours
through individual HTTP requests.

Run this from inside the `backend/` folder, with your venv active:
    python load_full_india_data.py

Place the 4 CSV files in the same folder as this script (or update the
paths below to point at wherever you kept them).
"""

import csv
import sys
import time

sys.path.insert(0, ".")  # so `database` and `models` import correctly

from database import SessionLocal, engine, Base
import models

Base.metadata.create_all(bind=engine)


def bulk_insert(db, rows, batch_size=2000):
    """Insert in batches — much faster than one commit per row."""
    total = 0
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        db.bulk_insert_mappings(models.DataSource, batch)
        db.commit()
        total += len(batch)
    return total


def load_flood_risk(db, path="flood_risk_india_clean.csv"):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            content = (
                f"Flood risk near {row['nearest_city_approx']}, {row['state_approx']}. "
                f"Rainfall: {row['rainfall_mm']}mm, Water level: {row['water_level_m']}m, "
                f"River discharge: {row['river_discharge_m3s']}m3/s, "
                f"Historical floods: {row['historical_floods']}, "
                f"Flood occurred: {row['flood_occurred']}."
            )
            rows.append({
                "name": f"FloodRisk-{row['nearest_city_approx']}",
                "source_type": "flood_risk",
                "raw_content": content,
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
            })
    n = bulk_insert(db, rows)
    print(f"Loaded {n} flood risk records (all India)")


def load_landslides(db, path="landslides_india_clean.csv"):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            content = (
                f"Landslide at {row['location_description']} ({row['region']}) "
                f"on {row['event_date']}. Category: {row['landslide_category']}, "
                f"Trigger: {row['trigger']}, Size: {row['size']}, "
                f"Fatalities: {row['fatality_count']}. Source: {row['source_name']}."
            )
            rows.append({
                "name": f"Landslide-{row['event_id']}",
                "source_type": "landslide",
                "raw_content": content,
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
            })
    n = bulk_insert(db, rows)
    print(f"Loaded {n} landslide records (all India)")


def load_earthquakes(db, path="earthquakes_clean.csv"):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            content = (
                f"Earthquake magnitude {row['magnitude']} at {row['location']} "
                f"on {row['origin_time_utc']}. Depth: {row['depth_km']}km. "
                f"Status: {row['review_status']}. {row['felt_report']}."
            )
            rows.append({
                "name": f"Earthquake-{row['origin_time_utc']}",
                "source_type": "earthquake",
                "raw_content": content,
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
            })
    n = bulk_insert(db, rows)
    print(f"Loaded {n} earthquake records (all India)")


def load_weather(db, path="india_daily_weather_clean.csv"):
    """91,000+ rows — this is the big one, batched inserts keep it fast."""
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            content = (
                f"Weather in {row['city']}, {row['state']} on {row['date']}: "
                f"{row['weather_description']}. Max/Min temp: "
                f"{row['temperature_max_c']}C/{row['temperature_min_c']}C, "
                f"Rain: {row['rain_sum_mm']}mm, Wind: {row['wind_speed_max_kmh']}km/h."
            )
            rows.append({
                "name": f"Weather-{row['city']}-{row['date']}",
                "source_type": "weather",
                "raw_content": content,
                "latitude": None,   # dataset has no lat/lon, only city/state
                "longitude": None,
            })
    n = bulk_insert(db, rows)
    print(f"Loaded {n} weather records (all India)")


def load_user_reports(db, path="user_reports_clean.json"):
    import json
    rows = []
    with open(path, encoding="utf-8") as f:
        reports = json.load(f)
    for r in reports:
        content = (
            f"User report {r['report_id']}: severity {r['severity']}, "
            f"water level {r['water_level_cm']}cm, at {r['timestamp_utc']}."
        )
        rows.append({
            "name": f"UserReport-{r['report_id']}",
            "source_type": "user_report",
            "raw_content": content,
            "latitude": r.get("latitude"),
            "longitude": r.get("longitude"),
        })
    n = bulk_insert(db, rows)
    print(f"Loaded {n} user report records")


if __name__ == "__main__":
    start = time.time()
    db = SessionLocal()
    try:
        load_flood_risk(db)
        load_landslides(db)
        load_earthquakes(db)
        load_weather(db)
        load_user_reports(db)
    finally:
        db.close()
    print(f"Done. Total time: {round(time.time() - start, 1)}s")
