#!/usr/bin/env python
"""
Integration test script to verify D1 and D9 refined endpoints work correctly.
Sample birth data for Hemant Rathore.
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:5000/api/v1"

# Sample birth data
sample_data = {
    "name": "Hemant Rathore",
    "datetime": "1987-05-04T19:43:00",
    "latitude": 26.14093550,
    "longitude": 91.79102650,
    "timezone": 5.5,
    "place": "Dispur",
    "religion": "Hindu"
}

def test_endpoint(endpoint_name, url):
    """Test an endpoint and print the response."""
    print(f"\n{'='*60}")
    print(f"Testing: {endpoint_name}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(url, json=sample_data, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        try:
            data = response.json()
            print(f"Response:\n{json.dumps(data, indent=2, ensure_ascii=False)}")
        except:
            print(f"Raw Response:\n{response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
        print(f"Make sure Flask app is running on http://localhost:5000")

if __name__ == "__main__":
    print("\nVedic Astrology API - Endpoint Test")
    print(f"Sample Data: {json.dumps(sample_data, indent=2)}")
    
    # Test D1 Chart Refined
    test_endpoint("D1 Chart (Refined)", f"{BASE_URL}/d1-chart-refined")
    
    # Small delay
    time.sleep(1)
    
    # Test D9 Chart Refined
    test_endpoint("D9 Chart (Refined)", f"{BASE_URL}/d9-chart-refined")
    
    print(f"\n{'='*60}")
    print("Test complete!")
    print(f"{'='*60}\n")
