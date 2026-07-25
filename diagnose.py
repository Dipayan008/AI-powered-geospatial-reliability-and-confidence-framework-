import os

LAT, LON = 22.5726, 88.3639

print("=== Environment check ===")
print("OPENWEATHER_API_KEY set:", bool(os.environ.get("OPENWEATHER_API_KEY")))
print("SENTINELHUB_CLIENT_ID set:", bool(os.environ.get("SENTINELHUB_CLIENT_ID")))
print("SENTINELHUB_CLIENT_SECRET set:", bool(os.environ.get("SENTINELHUB_CLIENT_SECRET")))
print()

print("=== OpenWeather ===")
try:
    from ai.adapters.openweather import fetch_weather_observation
    result = fetch_weather_observation(LAT, LON)
    print("SUCCESS:", result)
except Exception as e:
    print("FAILED:", type(e).__name__, "-", e)
print()

print("=== OSM ===")
try:
    from ai.adapters.osm import fetch_osm_observation
    result = fetch_osm_observation(LAT, LON)
    print("SUCCESS:", result)
except Exception as e:
    print("FAILED:", type(e).__name__, "-", e)
print()

print("=== Sentinel-2 ===")
try:
    from ai.adapters.sentinel import fetch_sentinel_observation
    result = fetch_sentinel_observation(LAT, LON)
    print("SUCCESS:", result)
except Exception as e:
    print("FAILED:", type(e).__name__, "-", e)
