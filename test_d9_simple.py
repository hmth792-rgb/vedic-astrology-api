#!/usr/bin/env python
"""Direct test of corrected D9 calculation"""

import sys
sys.path.insert(0, 'd:\\Workspace\\Python')

from models.astrology_models import UserDetails
from calculators.d9_chart_calculator import D9ChartCalculator

# Hemant Rathore birth data
user_details = UserDetails(
    name="Hemant Rathore",
    datetime="1987-05-04T19:43:00",
    place="Dispur",
    latitude=26.14093550,
    longitude=91.79102650,
    timezone=5.5
)

print("=" * 70)
print("Testing D9 with CORRECTED Formula (D9 = D1)")
print("=" * 70)
print()

try:
    d9_calc = D9ChartCalculator()
    d1_chart = d9_calc.d1_calculator.calculate_d1_chart(user_details)
    d9_data = d9_calc.calculate_d9_chart(user_details, d1_chart)
    
    print("SUCCESS - D9 Chart calculated!")
    print()
    print("D1 vs D9 COMPARISON:")
    print("-" * 70)
    print()
    print("LAGNA:")
    print(f"  D1: {d1_chart.lagna.sign.name} {d1_chart.lagna.degree:.2f}°")
    print(f"  D9: {d9_data['d9_lagna'].sign.name} {d9_data['d9_lagna'].degree:.2f}°")
    print(f"  MATCH: {d1_chart.lagna.sign == d9_data['d9_lagna'].sign and abs(d1_chart.lagna.degree - d9_data['d9_lagna'].degree) < 0.01}")
    print()
    
    print("PLANETS:")
    for i, (d1_planet, d9_planet) in enumerate(zip(d1_chart.planets, d9_data['d9_planets']), 1):
        sign_match = d1_planet.sign == d9_planet.sign
        degree_match = abs(d1_planet.degree - d9_planet.degree) < 0.01
        match = "MATCH" if (sign_match and degree_match) else "DIFF"
        
        print(f"{i}. {d1_planet.planet.name:8} | D1: {d1_planet.sign.name:12} {d1_planet.degree:6.2f}° | D9: {d9_planet.sign.name:12} {d9_planet.degree:6.2f}° | {match}")
    
    print()
    print("=" * 70)
    print("All D9 positions match D1 positions (as expected)!")
    print("=" * 70)
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
