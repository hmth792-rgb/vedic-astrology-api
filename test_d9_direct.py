#!/usr/bin/env python
"""Direct test of D9 calculation without HTTP"""

import sys
sys.path.insert(0, 'd:\\Workspace\\Python')

from models.astrology_models import UserDetails
from calculators.d9_chart_calculator import D9ChartCalculator
import json

# Create user details for Hemant Rathore
user_details = UserDetails(
    name="Hemant Rathore",
    datetime="1987-05-04T19:43:00",
    place="Dispur",
    latitude=26.1445,
    longitude=91.7362,
    timezone=5.5  # India Standard Time (UTC+5:30)
)

print("=" * 70)
print("Testing D9 Chart Calculation with Corrected Formula (Direct)")
print("=" * 70)
print()
print("Birth Details:")
print(f"  Name: {user_details.name}")
print(f"  Date/Time: {user_details.datetime}")
print(f"  Place: {user_details.place}")
print()

try:
    # Calculate D9 chart
    d9_calc = D9ChartCalculator()
    d9_data = d9_calc.calculate_d9_chart(user_details)
    
    print("✓ D9 Chart calculated successfully!")
    print()
    
    # Display Lagna
    lagna = d9_data["d9_lagna"]
    print("LAGNA (Ascendant):")
    print(f"  Sign: {lagna.sign.name}")
    print(f"  Degree: {lagna.degree:.2f}°")
    print(f"  Longitude: {lagna.longitude:.6f}°")
    print(f"  Nakshatra: {lagna.nakshatra}")
    print(f"  Pada: {lagna.nakshatra_pada}")
    print()
    
    # Display planets
    print("GRAHAS (Planets):")
    print()
    
    for i, planet in enumerate(d9_data["d9_planets"], 1):
        print(f"{i}. {planet.planet.name}:")
        print(f"   Sign: {planet.sign.name} ({planet.degree:.2f}°)")
        print(f"   Nakshatra: {planet.nakshatra} Pada {planet.nakshatra_pada}")
        print(f"   Longitude: {planet.longitude:.6f}°")
        print(f"   Retrograde: {planet.retrograde}")
        print()
    
    print("=" * 70)
    print(f"Ayanamsa: {d9_data['ayanamsa']:.6f}°")
    print("=" * 70)
    print()
    print("✓ D9 Chart calculation completed successfully!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
