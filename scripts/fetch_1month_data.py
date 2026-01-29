#!/usr/bin/env python3
"""
Fetch last 1 month of M4.5+ earthquake data globally from USGS.
Saves to data/earthquakes_1month.json
"""
import requests
import json
from datetime import datetime, timedelta

MINMAG = 4.5

def fetch_1month_data():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "geojson",
        "starttime": start_date.strftime("%Y-%m-%d"),
        "endtime": end_date.strftime("%Y-%m-%d"),
        "minmagnitude": MINMAG,
        "orderby": "time-asc"
    }
    
    print(f"Fetching global earthquakes from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
    response = requests.get(url, params=params, timeout=120)
    response.raise_for_status()
    data = response.json()
    
    count = len(data.get("features", []))
    print(f"  Found {count} earthquakes")
    
    with open("data/earthquakes_1month.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    
    print("Saved to data/earthquakes_1month.json")
    return count

if __name__ == "__main__":
    fetch_1month_data()
