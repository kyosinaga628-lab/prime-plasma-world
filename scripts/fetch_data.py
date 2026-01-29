import requests
import json
from datetime import datetime, timedelta

def fetch_earthquake_data():
    # Define time range: 1 year ago to now
    end_time = datetime.now()
    start_time = end_time - timedelta(days=365)
    
    # Format dates to ISO 8601
    start_str = start_time.strftime('%Y-%m-%dT%H:%M:%S')
    end_str = end_time.strftime('%Y-%m-%dT%H:%M:%S')
    
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    
    # Global earthquakes - no geographic limit, M4.5+ to manage data volume
    params = {
        "format": "geojson",
        "starttime": start_str,
        "endtime": end_str,
        "minmagnitude": 4.5,  # M4.5+ for global (higher threshold due to larger dataset)
        "orderby": "time"
    }
    
    print(f"Fetching global earthquake data from USGS ({start_str} to {end_str})...")
    try:
        response = requests.get(url, params=params, timeout=120)
        response.raise_for_status()
        data = response.json()
        
        count = data.get('metadata', {}).get('count', 0)
        print(f"Successfully fetched {count} earthquake events.")
        
        output_path = "data/earthquakes.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"Data saved to {output_path}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    fetch_earthquake_data()
