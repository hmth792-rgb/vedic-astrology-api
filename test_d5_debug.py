"""
Debug script to test D5 calculation for specific birth data
"""
from datetime import datetime
from models.astrology_models import UserDetails
from calculators.d1_chart_calculator import D1ChartCalculator
from calculators.d5_chart_calculator import D5ChartCalculator

# Birth data
user_details = UserDetails(
    name="Hemant Rathore",
    datetime="1987-05-04T19:43:00",
    latitude=26.14,
    longitude=91.79,
    timezone=5.5,
    place="Dispur"
)

# Initialize calculators
d1_calc = D1ChartCalculator(ephe_path="./ephe")
d5_calc = D5ChartCalculator(ephe_path="./ephe")

# Calculate D1 chart
d1_chart = d1_calc.calculate_d1_chart(user_details)

print("=" * 80)
print("D1 CHART POSITIONS (Base Chart)")
print("=" * 80)
print(f"Lagna: {d1_chart.lagna.longitude:.2f}° ({d1_chart.lagna.sign.name})")

for planet in d1_chart.planets:
    print(f"{planet.planet.name:10s}: {planet.longitude:8.2f}° ({planet.sign.name:12s}) - {planet.nakshatra.name if planet.nakshatra else 'N/A'}")

print("\n" + "=" * 80)
print("D5 CHART POSITIONS")
print("=" * 80)

# Calculate D5 chart
d5_data = d5_calc.calculate_d5_chart(user_details, d1_chart)
print(f"Lagna: {d5_data['lagna'].longitude:.2f}° ({d5_data['lagna'].sign.name})")

for planet in d5_data['planets']:
    print(f"{planet.planet.name:10s}: {planet.longitude:8.2f}° ({planet.sign.name:12s}) - {planet.nakshatra.name if planet.nakshatra else 'N/A'}")

print("\n" + "=" * 80)
print("DETAILED COMPARISON")
print("=" * 80)

expected_d5 = {
    "Lagna": (11, 10, "PISCES", "Uttara Bhadrapada 3"),
    "SUN": (2, 9, "GEMINI", "Ardra 1"),
    "MOON": (1, 16, "TAURUS", "Rohini 3"),
    "MARS": (7, 7, "SCORPIO", "Anuradha 2"),
    "MERCURY": (8, 22, "SAGITTARIUS", "Purva Ashadha 3"),
    "JUPITER": (9, 16, "CAPRICORN", "Shravana 2"),
    "VENUS": (9, 13, "CAPRICORN", "Shravana 2"),
    "SATURN": (7, 12, "SCORPIO", "Anuradha 3"),
    "RAHU": (11, 21, "PISCES", "Revati 2"),
    "KETU": (11, 21, "PISCES", "Revati 2"),
}

for planet in d5_data['planets']:
    name = planet.planet.name
    actual_sign = planet.sign.value - 1  # Convert to 0-11
    actual_deg = planet.degree
    
    if name in expected_d5:
        exp_sign, exp_deg, exp_sign_name, exp_nak = expected_d5[name]
        match = "✅" if (actual_sign == exp_sign and abs(actual_deg - exp_deg) < 2) else "❌"
        print(f"{match} {name:10s}: D5={actual_sign:2d} ({planet.sign.name:12s}) {actual_deg:5.1f}° | Expected={exp_sign:2d} ({exp_sign_name:12s}) {exp_deg:2d}°")

# Check Lagna separately
lagna_sign = d5_data['lagna'].sign.value - 1
lagna_deg = d5_data['lagna'].degree
exp_sign, exp_deg, exp_sign_name, exp_nak = expected_d5["Lagna"]
match = "✅" if (lagna_sign == exp_sign and abs(lagna_deg - exp_deg) < 2) else "❌"
print(f"{match} {'Lagna':10s}: D5={lagna_sign:2d} ({d5_data['lagna'].sign.name:12s}) {lagna_deg:5.1f}° | Expected={exp_sign:2d} ({exp_sign_name:12s}) {exp_deg:2d}°")
