"""
Test Whole Sign house calculations for Hemant Rathore
"""
import sys
sys.path.append('.')

from models.astrology_models import UserDetails
from calculators.d1_chart_calculator import D1ChartCalculator

# Test data for Hemant Rathore
user_details = UserDetails(
    name="Hemant Rathore",
    datetime="1987-05-04T19:43:00",
    latitude=26.14093550,
    longitude=91.79102650,
    timezone="Asia/Kolkata",
    place="Dispur",
    religion="Hindu"
)

print("="*80)
print("Testing D1 Chart with Whole Sign Houses")
print("="*80)
print()

calculator = D1ChartCalculator(ephe_path="./ephe")
d1_chart = calculator.calculate_d1_chart(user_details)

print(f"Lagna: {d1_chart.lagna.degree:.2f}° {d1_chart.lagna.sign.name}")
print(f"Ayanamsa: {d1_chart.ayanamsa:.6f}")
print()

print("PLANETARY POSITIONS AND HOUSES:")
print("-"*80)
print(f"{'Planet':<12} {'Sign':<15} {'Longitude':<12} {'House':<8} {'Expected':<10}")
print("-"*80)

expected = {
    "SUN": 6,
    "MOON": 9,
    "MERCURY": 6,
    "VENUS": 5,
    "MARS": 7,
    "JUPITER": 5,
    "SATURN": 1,
    "RAHU": 5,
    "KETU": 11
}

for planet in d1_chart.planets:
    name = planet.planet.name
    sign = planet.sign.name
    house = planet.is_in_house if planet.is_in_house else "-"
    exp_house = expected.get(name, "-")
    match = "✓" if house == exp_house else "✗ MISMATCH"
    
    print(f"{name:<12} {sign:<15} {planet.longitude:>6.2f}° {house:>4} {exp_house:>8} {match}")

print()
print("="*80)
print("HOUSE RESIDENTS:")
print("="*80)

for house in d1_chart.houses:
    residents = ", ".join([p.name for p in house.planets_in_house]) if house.planets_in_house else "empty"
    print(f"House {house.house_number:2d} ({house.sign.name:12s}): {residents}")

print()
print("Expected placements according to manual data:")
print("  House 1: SATURN")
print("  House 5: VENUS, JUPITER, RAHU")
print("  House 6: SUN, MERCURY")
print("  House 7: MARS")
print("  House 9: MOON")
print("  House 11: KETU")
