"""
Test script for timezone offset format
Tests the API with numeric timezone offset instead of timezone string
"""
import requests
import json

# API endpoint
BASE_URL = "http://127.0.0.1:5000"

# Test data with numeric timezone offset
test_data = {
    "name": "Hemant Rathore",
    "datetime": "1987-05-04T19:43:00",
    "latitude": 26.14093550,
    "longitude": 91.79102650,
    "timezone": 5.5,  # IST = UTC+5:30 = +5.5 hours
    "place": "Dispur",
    "religion": "Hindu"
}

print("=" * 80)
print("Testing Timezone Offset Format")
print("=" * 80)
print("\n📋 Request Body:")
print(json.dumps(test_data, indent=2))

# Test Refined Endpoint
print("\n" + "=" * 80)
print("1. Testing REFINED Endpoint: /api/v1/d1-chart-refined")
print("=" * 80)

try:
    response = requests.post(
        f"{BASE_URL}/api/v1/d1-chart-refined",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\n✅ Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n📊 Refined Chart Response:")
        print(json.dumps(data, indent=2))
        
        # Verify house placements
        if "data" in data and "grahas" in data["data"]:
            print("\n🔍 House Verification:")
            print(f"{'Planet':<15} {'House':<8} {'Expected':<10} {'Match'}")
            print("-" * 50)
            
            expected_houses = {
                "☉Sun": 6,
                "☽Moon": 9,
                "☿Mercury": 6,
                "♀Venus": 5,
                "♂Mars": 7,
                "♃Jupiter": 5,
                "♄Saturn": 1,
                "☊Rahu": 5,
                "☋Ketu": 11
            }
            
            for graha in data["data"]["grahas"]:
                if graha["graha"] == "Lagna":
                    continue
                    
                graha_name = graha["graha"]
                house = graha["in"]
                expected = expected_houses.get(graha_name, "-")
                match = "✅" if house == expected else "❌"
                
                print(f"{graha_name:<15} {house:<8} {expected:<10} {match}")
    else:
        print(f"\n❌ Error Response:")
        print(json.dumps(response.json(), indent=2))
        
except Exception as e:
    print(f"\n❌ Request failed: {str(e)}")

# Test Full Endpoint
print("\n" + "=" * 80)
print("2. Testing FULL Endpoint: /api/v1/d1-chart")
print("=" * 80)

try:
    response = requests.post(
        f"{BASE_URL}/api/v1/d1-chart",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\n✅ Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n📊 Full Chart Response (abbreviated):")
        
        # Print only key information
        if "data" in data:
            chart_data = data["data"]
            
            if "lagna" in chart_data:
                print(f"\n🏠 Lagna: {chart_data['lagna']['long']}")
            
            if "grahas" in chart_data:
                print(f"\n🪐 Planets ({len(chart_data['grahas'])} planets):")
                for planet in chart_data["grahas"][:3]:  # Show first 3
                    print(f"  - {planet['graha']}: House {planet['in']}, {planet['long']}")
            
            if "ayanamsa" in chart_data:
                print(f"\n🌟 Ayanamsa: {chart_data['ayanamsa']}")
    else:
        print(f"\n❌ Error Response:")
        print(json.dumps(response.json(), indent=2))
        
except Exception as e:
    print(f"\n❌ Request failed: {str(e)}")

print("\n" + "=" * 80)
print("✅ Timezone Offset Tests Complete!")
print("=" * 80)
