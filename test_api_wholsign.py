"""
Test the updated API with Whole Sign houses
"""
import requests
import json

# Test data for Hemant Rathore
test_data = {
    "name": "Hemant Rathore",
    "datetime": "1987-05-04T19:43:00",
    "latitude": 26.14093550,
    "longitude": 91.79102650,
    "timezone": "Asia/Kolkata",
    "place": "Dispur",
    "religion": "Hindu"
}

print("="*80)
print("Testing Astrology API with Whole Sign Houses")
print("="*80)
print()

# Test refined endpoint
print("1. Testing REFINED endpoint (api/v1/d1-chart-refined)")
print("-"*80)

try:
    response = requests.post("http://127.0.0.1:5000/api/v1/d1-chart-refined", json=test_data)
    
    if response.status_code == 200:
        data = response.json()["data"]
        
        print("\nGRAHAS (Simplified):")
        for g in data["grahas"]:
            print(f"  {g['graha']:15s} {g['long']:20s} House {g['in']:2}")
        
        print("\nBHAVAS (Simplified):")
        for b in data["bhavas"]:
            print(f"  House {b['no']:2d} ({b['rashi']:12s}): {b['res']}")
        
        print(f"\nAyanamsa: {data['ayanamsa']}")
        print("\n✓ Refined endpoint working!")
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"✗ Error: {e}")

print()
print("="*80)
print("2. Testing FULL endpoint (api/v1/d1-chart)")
print("-"*80)

try:
    response = requests.post("http://127.0.0.1:5000/api/v1/d1-chart", json=test_data)
    
    if response.status_code == 200:
        data = response.json()["data"]
        
        print("\nLAGNA:")
        print(f"  {data['lagna']['graha']}: {data['lagna']['long']} ({data['lagna']['sign']})")
        
        print("\nGRAHAS (Complete):")
        for g in data["grahas"][:3]:  # Show first 3
            print(f"  {g['graha']:15s} {g['long']:20s} House {g['in']:2} | Rel: {g['rel']}")
        print("  ... (more planets)")
        
        print("\nBHAVAS (Complete):")
        for b in data["bhavas"][:3]:  # Show first 3
            print(f"  House {b['no']:2d}: Residents={b['res']}, Owner={b['own']}, Aspected by={b['asp']}")
        print("  ... (more houses)")
        
        print(f"\nAyanamsa: {data['ayanamsa']}")
        print("\n✓ Full endpoint working!")
        
        # Verify house placements
        print("\n" + "="*80)
        print("VERIFICATION AGAINST EXPECTED VALUES:")
        print("="*80)
        
        expected_houses = {
            "Sun": 6,
            "Moon": 9,
            "Mercury": 6,
            "Venus": 5,
            "Mars": 7,
            "Jupiter": 5,
            "Saturn": 1,
            "Rahu": 5,
            "Ketu": 11
        }
        
        all_match = True
        for g in data["grahas"]:
            planet_name = g["graha"].split()[0].replace("☉", "").replace("☾", "").replace("♂", "").replace("☿", "").replace("♃", "").replace("♀", "").replace("♄", "").replace("☊", "").replace("☋", "")
            if planet_name in expected_houses:
                expected = expected_houses[planet_name]
                actual = g["in"]
                match = "✓" if expected == actual else "✗"
                print(f"  {planet_name:10s}: Expected House {expected:2}, Got House {actual:2} {match}")
                if expected != actual:
                    all_match = False
        
        if all_match:
            print("\n🎉 ALL HOUSES MATCH CORRECTLY!")
        else:
            print("\n⚠ Some house placements don't match")
            
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"✗ Error: {e}")
