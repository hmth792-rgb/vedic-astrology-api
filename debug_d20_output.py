"""
Debug script to check D20 chart output for Hemant Rathore
and compare with expected data
"""
from models.astrology_models import UserDetails, Planet, Zodiac
from calculators.d20_chart_calculator import D20ChartCalculator
from calculators.d1_chart_calculator import D1ChartCalculator
from utils.vedic_helper import VedicAstrologyHelper

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
d20_calc = D20ChartCalculator(ephe_path="./ephe")

# Calculate charts
d1_chart = d1_calc.calculate_d1_chart(user_details)
d20_chart = d20_calc.calculate_d20_chart(user_details, d1_chart)

print("=" * 100)
print("D1 CHART (Base Chart - for reference)")
print("=" * 100)
print(f"\nLagna: {d1_chart.lagna.longitude:.4f}° ({d1_chart.lagna.sign.name}), Degree: {d1_chart.lagna.degree:.2f}°")
for planet in d1_chart.planets:
    print(f"{planet.planet.name:10s}: {planet.longitude:.4f}° ({planet.sign.name}), Degree: {planet.degree:.2f}°")

print("\n" + "=" * 100)
print("D20 CHART (Vimshamsha) - Current Calculation")
print("=" * 100)

# Display Lagna
lagna = d20_chart['lagna']
print(f"\nLagna: {lagna.longitude:.4f}° ({lagna.sign.name}), Degree: {lagna.degree:.2f}°")
if lagna.nakshatra:
    print(f"  Nakshatra: {lagna.nakshatra.name}, Pada: {lagna.nakshatra_pada}")
if lagna.nakshatra_lord:
    print(f"  Nakshatra Lord: {lagna.nakshatra_lord.name}")

# Display Planets
print("\nPlanets:")
planet_order = [
    Planet.SUN, Planet.MOON, Planet.MARS, Planet.MERCURY,
    Planet.JUPITER, Planet.VENUS, Planet.SATURN, Planet.RAHU, Planet.KETU
]

helper = VedicAstrologyHelper()

for planet_enum in planet_order:
    planet = next((p for p in d20_chart['planets'] if p.planet == planet_enum), None)
    if planet:
        retrograde_mark = " (R)" if planet.retrograde else ""
        sign_short = helper.get_sign_short_name(planet.sign)
        degree_in_sign = planet.degree
        minutes = int((degree_in_sign - int(degree_in_sign)) * 60)
        seconds = int(((degree_in_sign - int(degree_in_sign)) * 60 - minutes) * 60)
        
        nak_name = planet.nakshatra.name.replace('_', ' ').title() if planet.nakshatra else "-"
        ruler_of = ", ".join([str(h) for h in planet.ruler_of_houses]) if planet.ruler_of_houses else "-"
        is_in = planet.is_in_house if planet.is_in_house else "-"
        
        print(f"\n{planet.planet.name}{retrograde_mark}:")
        print(f"  Longitude: {int(planet.degree)}° {sign_short} {minutes:02d}′ {seconds:02d}″")
        print(f"  Full Longitude: {planet.longitude:.4f}°")
        print(f"  Nakshatra: {nak_name} {planet.nakshatra_pada if planet.nakshatra else ''}")
        print(f"  Nakshatra Lord: {planet.nakshatra_lord.name if planet.nakshatra_lord else '-'}")
        print(f"  Sub Lord: {planet.sub_lord.name if planet.sub_lord else '-'}")
        print(f"  Ruler of Houses: {ruler_of}")
        print(f"  Is In House: {is_in}")
        print(f"  House Owner: {planet.house_owner.name if planet.house_owner else '-'}")
        print(f"  Relationship: {planet.relationship if planet.relationship else '-'}")
        print(f"  Dignity: {planet.dignity if planet.dignity else '-'}")

# Display Houses
print("\n" + "=" * 100)
print("D20 HOUSES")
print("=" * 100)
for house in d20_chart['houses']:
    planets_in = [p.name for p in house.planets_in_house]
    print(f"House {house.house_number}: {house.sign.name} (Lord: {house.ruler_planet.name if house.ruler_planet else '-'}) - Planets: {planets_in if planets_in else 'None'}")

print("\n" + "=" * 100)
print("AYANAMSA")
print("=" * 100)
print(f"Ayanamsa: {d20_chart['ayanamsa']:.6f}°")
