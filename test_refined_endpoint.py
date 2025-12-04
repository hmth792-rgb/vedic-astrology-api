"""
Test the refined D1 chart endpoint
"""
import requests
import json

# API endpoint
url = "http://127.0.0.1:5000/api/v1/d1-chart-refined"

# Test data - September 29, 1989, New Delhi
test_data = {
    "name": "Test Person",
    "datetime": "1989-09-29T23:00:00",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "timezone": "Asia/Kolkata",
    "place": "New Delhi, India",
    "religion": "Hindu"
}

print("Testing Refined D1 Chart Endpoint")
print("="*70)
print(f"URL: {url}")
print(f"Request Data: {json.dumps(test_data, indent=2)}")
print("="*70)
print()

try:
    response = requests.post(url, json=test_data)
    
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        
        print("GRAHA TABLE (Simplified):")
        print("-"*70)
        
        if 'data' in data and 'graha_table' in data['data']:
            for graha in data['data']['graha_table']:
                print(f"\nGraha: {graha['graha']}")
                print(f"  Longitude: {graha['longitude']}")
                print(f"  Nakshatra: {graha['nakshatra']} - Pada {graha['nakshatra_pada']}")
                print(f"  Lord/Sub Lord: {graha['lord_sub_lord']}")
                print(f"  Ruler of: {graha['ruler_of']}")
                print(f"  Is In: {graha['is_in']}")
                print(f"  Bhava Owner: {graha['bhava_owner']}")
                print(f"  Relationship: {graha['relationship']}")
                print(f"  Dignity: {graha['dignity']}")
        
        print()
        print("="*70)
        print("BHAVA TABLE (Simplified):")
        print("-"*70)
        
        if 'data' in data and 'bhava_table' in data['data']:
            for bhava in data['data']['bhava_table']:
                print(f"\nBhava {bhava['bhava']} ({bhava['rashi']}):")
                print(f"  Residents: {bhava['residents']}")
                print(f"  Owner: {bhava['owner']}")
                print(f"  Qualities: {bhava['qualities']}")
                print(f"  Aspected By: {bhava['aspected_by']}")
        
        print()
        print("="*70)
        print(f"Ayanamsa: {data['data']['ayanamsa']}")
        print(f"Calculation Time: {data['data']['calculation_time']}")
        
    else:
        print(f"Error: {response.text}")

except Exception as e:
    print(f"Error: {str(e)}")
