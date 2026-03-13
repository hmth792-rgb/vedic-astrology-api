"""
Test D20 chart endpoint to see formatted output
"""
import json
from models.astrology_models import UserDetails
from calculators.d1_chart_calculator import D1ChartCalculator
from calculators.d20_chart_calculator import D20ChartCalculator
from routes.d20_routes import _format_refined_response

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

# Format response
response = _format_refined_response(d20_chart, "./ephe")

print("=" * 120)
print("FORMATTED D20 CHART RESPONSE (Dynamic Data)")
print("=" * 120)
print(json.dumps(response, indent=2, ensure_ascii=False))
