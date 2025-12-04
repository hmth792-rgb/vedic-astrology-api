"""
Test refined endpoint - graha details only with correct sequence
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

# Test data
test_data = {
    "name": "Hemant Rathore",
    "datetime": "1987-05-04T19:43:00",
    "latitude": 26.14093550,
    "longitude": 91.79102650,
    "timezone": 5.5,
    "place": "Dispur",
    "religion": "Hindu"
}

print("=" * 100)
print("Testing REFINED Endpoint - Graha Details Only (Correct Sequence)")
print("=" * 100)

try:
    response = requests.post(
        f"{BASE_URL}/api/v1/d1-chart-refined",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\n✅ Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n📋 Response Structure:")
        print(json.dumps(data, indent=2))
        
        # Verify sequence
        if "data" in data and "grahas" in data["data"]:
            grahas = data["data"]["grahas"]
            print("\n" + "=" * 100)
            print("GRAHA SEQUENCE VERIFICATION")
            print("=" * 100)
            
            expected_sequence = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
            
            print(f"\n{'#':<3} {'Expected':<15} {'Actual':<20} {'Match'}")
            print("-" * 60)
            
            for i, expected_graha in enumerate(expected_sequence):
                if i < len(grahas):
                    actual_graha = grahas[i]["graha"].split()[0]  # Extract graha name without symbol
                    match = "✅" if expected_graha.lower() in grahas[i]["graha"].lower() else "❌"
                    print(f"{i+1:<3} {expected_graha:<15} {grahas[i]['graha']:<20} {match}")
                else:
                    print(f"{i+1:<3} {expected_graha:<15} {'MISSING':<20} ❌")
            
            # Sample data display
            print("\n" + "=" * 100)
            print("SAMPLE DATA (First 3 Grahas)")
            print("=" * 100)
            for i, graha in enumerate(grahas[:3]):
                print(f"\n{i+1}. {graha['graha']}")
                print(f"   Longitude: {graha['long']}")
                print(f"   Nakshatra: {graha['nak']}")
                print(f"   Lord/Sub-Lord: {graha['lord']}")
                print(f"   Rules: {graha['rules']}")
                print(f"   In House: {graha['in']}")
                print(f"   House Owner: {graha['owner']}")
                print(f"   Relationship: {graha['rel']}")
                print(f"   Dignity: {graha['dig']}")
    else:
        print(f"\n❌ Error Response:")
        print(json.dumps(response.json(), indent=2))
        
except Exception as e:
    print(f"\n❌ Request failed: {str(e)}")

print("\n" + "=" * 100)
