#!/usr/bin/env python
"""Test D9 Chart API with Hemant Rathore birth data from Dispur"""

import requests
import json
from datetime import datetime

# API endpoint
url = "http://127.0.0.1:5000/api/v1/d9-chart-refined"

# Hemant Rathore birth data
payload = {
    "name": "Hemant Rathore",
    "datetime": "1987-05-04T19:43:00",
    "place": "Dispur",
    "latitude": 26.1445,
    "longitude": 91.7362,
    "timezone": "+05:30"
}

print("=" * 70)
print("Testing D9 Chart Calculation with Corrected Formula")
print("=" * 70)
print()
print("Birth Details:")
print(f"  Name: {payload['name']}")
print(f"  Date: {payload['datetime'][:10]}")
print(f"  Time: {payload['datetime'][11:]}")
print(f"  Place: {payload['place']}")
print()
print(f"Sending request to: {url}")
print()

try:
    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    data = response.json()
    
    print("✓ Response received successfully!")
    print()
    print("=" * 70)
    print("LAGNA (Ascendant)")
    print("=" * 70)
    
    lagna = data.get("Lagna", {})
    print(f"  Graha: {lagna.get('Graha')}")
    print(f"  Rashi: {lagna.get('Rashi')} ({lagna.get('Rashi_Short')})")
    print(f"  Degree: {lagna.get('Degree')}°")
    print(f"  Longitude: {lagna.get('Longitude')}°")
    print(f"  Nakshatra: {lagna.get('Nakshatra')} Pada {lagna.get('Pada')}")
    print(f"  Nakshatra Lord: {lagna.get('Nakshatra_Lord')}")
    print(f"  Sub Lord: {lagna.get('Sub_Lord')}")
    print()
    
    print("=" * 70)
    print("GRAHAS (Planets)")
    print("=" * 70)
    print()
    
    planets = ["Surya", "Chandra", "Mangal", "Budha", "Guru", "Shukra", "Shani", "Rahu", "Ketu"]
    
    for planet_key in planets:
        if planet_key in data:
            planet = data[planet_key]
            print(f"{planet_key}:")
            print(f"  Rashi: {planet.get('Rashi')} ({planet.get('Rashi_Short')}) | Degree: {planet.get('Degree')}°")
            print(f"  Nakshatra: {planet.get('Nakshatra')} Pada {planet.get('Pada')}")
            print(f"  Longitude: {planet.get('Longitude')}°")
            print()
    
    print("=" * 70)
    print(f"Ayanamsa: {data.get('Ayanamsa')}°")
    print("=" * 70)
    print()
    print("✓ D9 Chart calculation completed successfully!")
    print()
    print("Full JSON Response:")
    print(json.dumps(data, indent=2))
    
except requests.exceptions.ConnectionError:
    print("❌ Error: Could not connect to Flask server at http://127.0.0.1:5000")
    print("   Make sure the Flask server is running: python app.py")
except requests.exceptions.RequestException as e:
    print(f"❌ Error: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response: {e.response.text}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
