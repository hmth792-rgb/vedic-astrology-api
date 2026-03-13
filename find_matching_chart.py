"""
Try different divisional charts to find which one matches the expected data
"""
from models.astrology_models import UserDetails, Planet
from calculators.d1_chart_calculator import D1ChartCalculator
from calculators.d2_chart_calculator import D2ChartCalculator
from calculators.d3_chart_calculator import D3ChartCalculator
from calculators.d4_chart_calculator import D4ChartCalculator
from calculators.d5_chart_calculator import D5ChartCalculator
from calculators.d6_chart_calculator import D6ChartCalculator
from calculators.d7_chart_calculator import D7ChartCalculator
from calculators.d8_chart_calculator import D8ChartCalculator
from calculators.d9_chart_calculator import D9ChartCalculator
from calculators.d10_chart_calculator import D10ChartCalculator
from calculators.d12_chart_calculator import D12ChartCalculator
from calculators.d16_chart_calculator import D16ChartCalculator
from calculators.d20_chart_calculator import D20ChartCalculator
from calculators.d24_chart_calculator import D24ChartCalculator
from calculators.d30_chart_calculator import D30ChartCalculator
from utils.vedic_helper import VedicAstrologyHelper

user_details = UserDetails(
    name="Hemant Rathore",
    datetime="1987-05-04T19:43:00",
    latitude=26.14,
    longitude=91.79,
    timezone=5.5,
    place="Dispur"
)

# Expected data from user
expected_lagna = "20° Mitu 03′ 44″"  # Mithuna (Gemini) 20°
expected_sun = "21° Kany 49′ 39″"    # Kanya (Virgo) 21°
expected_moon = "06° Vish 08′ 48″"   # Visha/Pisces 6° (incorrect sign, should be Virgo)

print("Expected Lagna: 20° Mithuna (Gemini) = ~50° absolute longitude")
print("Expected Sun: 21° Kanya (Virgo) = ~171° absolute longitude")
print("Expected Moon: 06° Visha (Pisces) = ~336° absolute longitude (or 06° Virgo = ~156°)")

helper = VedicAstrologyHelper()
d1_calc = D1ChartCalculator(ephe_path="./ephe")
d1_chart = d1_calc.calculate_d1_chart(user_details)

print("\n" + "=" * 80)
print("D1 (Base Chart)")
print("=" * 80)
print(f"D1 Lagna: {d1_chart.lagna.degree:.2f}° {d1_chart.lagna.sign.name} = {d1_chart.lagna.longitude:.2f}°")
print(f"D1 Sun: {d1_chart.planets[0].degree:.2f}° {d1_chart.planets[0].sign.name} = {d1_chart.planets[0].longitude:.2f}°")

# Try different divisional charts
charts_to_test = [
    ("D2", D2ChartCalculator),
    ("D3", D3ChartCalculator),
    ("D4", D4ChartCalculator),
    ("D5", D5ChartCalculator),
    ("D6", D6ChartCalculator),
    ("D7", D7ChartCalculator),
    ("D8", D8ChartCalculator),
    ("D9", D9ChartCalculator),
    ("D10", D10ChartCalculator),
    ("D12", D12ChartCalculator),
    ("D16", D16ChartCalculator),
    ("D20", D20ChartCalculator),
    ("D24", D24ChartCalculator),
    ("D30", D30ChartCalculator),
]

for chart_name, CalcClass in charts_to_test:
    try:
        calc = CalcClass(ephe_path="./ephe")
        chart = calc.calculate_d20_chart(user_details, d1_chart) if hasattr(calc, 'calculate_d20_chart') else None
        
        if chart is None:
            # Try other method names
            if hasattr(calc, 'calculate_d2_chart'):
                chart = calc.calculate_d2_chart(user_details, d1_chart)
            elif hasattr(calc, 'calculate_d3_chart'):
                chart = calc.calculate_d3_chart(user_details, d1_chart)
            elif hasattr(calc, 'calculate_d4_chart'):
                chart = calc.calculate_d4_chart(user_details, d1_chart)
            elif hasattr(calc, 'calculate_d5_chart'):
                chart = calc.calculate_d5_chart(user_details, d1_chart)
            elif hasattr(calc, 'calculate_d6_chart'):
                chart = calc.calculate_d6_chart(user_details, d1_chart)
            elif hasattr(calc, 'calculate_d7_chart'):
                chart = calc.calculate_d7_chart(user_details, d1_chart)
            elif hasattr(calc, 'calculate_d8_chart'):
                chart = calc.calculate_d8_chart(user_details, d1_chart)
            elif hasattr(calc, 'calculate_d9_chart'):
                chart = calc.calculate_d9_chart(user_details, d1_chart)
            elif hasattr(calc, 'calculate_d10_chart'):
                chart = calc.calculate_d10_chart(user_details, d1_chart)
            elif hasattr(calc, 'calculate_d12_chart'):
                chart = calc.calculate_d12_chart(user_details, d1_chart)
            elif hasattr(calc, 'calculate_d16_chart'):
                chart = calc.calculate_d16_chart(user_details, d1_chart)
            elif hasattr(calc, 'calculate_d24_chart'):
                chart = calc.calculate_d24_chart(user_details, d1_chart)
            elif hasattr(calc, 'calculate_d30_chart'):
                chart = calc.calculate_d30_chart(user_details, d1_chart)
        
        if chart:
            lagna = chart.get('lagna') or chart.get('d2_lagna') or chart.get('d9_lagna')
            planets = chart.get('planets') or chart.get('d2_planets') or chart.get('d9_planets')
            
            if lagna and planets:
                sun = next((p for p in planets if p.planet == Planet.SUN), None)
                
                lagna_deg = int(lagna.degree)
                lagna_min = int((lagna.degree - lagna_deg) * 60)
                sun_deg = int(sun.degree) if sun else 0
                sun_min = int((sun.degree - sun_deg) * 60) if sun else 0
                
                lagna_sign = helper.get_sign_short_name(lagna.sign)
                sun_sign = helper.get_sign_short_name(sun.sign) if sun else "-"
                
                print(f"\n{chart_name}: Lagna {lagna_deg}° {lagna_sign} ({lagna.longitude:.2f}°), Sun {sun_deg}° {sun_sign} ({sun.longitude:.2f}° if sun else '-')")
    except Exception as e:
        print(f"\n{chart_name}: Error - {str(e)[:50]}")
